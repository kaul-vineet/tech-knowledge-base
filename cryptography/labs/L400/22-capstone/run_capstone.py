"""Capstone: an encrypted document service, end to end on 127.0.0.1 with seeded faults. Prints one JSON line per
milestone and a final scorecard. Deterministic code decides every verdict; the agent only explains anomalies.
Run: python run_capstone.py   (add --real to let a local model explain; tests always use the fake server)."""
import base64
import json
import random
import sys
import tempfile
from pathlib import Path

import paths  # noqa: F401
import agent_explain
import agility_lint
import audit
import kms
import registry as reg
import service
import solution_mtls
import solution_verified
import test_fitness_no_key_export as l19_fitness
from doc_service import open_shared
from secrets_app import scan_log

SEED = 22
HERE = Path(__file__).resolve().parent


def m1_envelope_rotation(ns, rng) -> dict:
    for i in range(1, 7):
        ns.svc.put("alice", f"doc-{i}", f"contract {i}: price {rng.randrange(100, 999)}".encode(), readers=("bob", "mallory"))
        ns.clock.advance(1)
    ns.svc.rotate_kek()
    crash = rng.randrange(1, 4)
    try:
        ns.svc.rewrap(crash_after=crash)  # seeded crash part-way
    except RuntimeError:
        pass
    mixed = ns.svc.records_by_kid()
    try:
        ns.svc.retire(1)
        refused = False
    except PermissionError:
        refused = True
    resumed = ns.svc.rewrap()
    retired = ns.svc.retire(1)["retired"]
    readable = sum(1 for d in ns.svc.docs if ns.svc.get("alice", d).startswith(b"contract"))
    return {"milestone": "M1 envelope + versioned KEK + rotation", "crash_after": crash, "records_by_kid_after_crash": mixed,
            "retire_refused_while_in_use": refused, "resumed": resumed, "retired": retired, "readable": f"{readable}/6",
            "pass": refused and readable == 6}


def m2_mtls(ns) -> dict:
    results = {}
    for name, client in (("no client cert", kms.KMSClient(ns.port, ns.pki, with_cert=False)),
                         ("cert from another CA", kms.KMSClient(ns.port, solution_mtls.make_pki_with_client(ns.work / "rogue", "rogue"), ca_file=ns.pki / "ca.pem"))):
        try:
            client.call("rotate")
            results[name] = "accepted"
        except (OSError, PermissionError) as e:
            results[name] = f"refused ({type(e).__name__})"
    ok = ns.svc.get("bob", "doc-1").startswith(b"contract")
    return {"milestone": "M2 mTLS between doc service and KMS", "doc_service_client": "ok" if ok else "failed", **results,
            "pass": ok and all(v.startswith("refused") for v in results.values())}


def m3_audit(ns, rng) -> tuple:
    for i in range(1, 7):  # insider: mallory reads every document within 30 s
        ns.svc.get("mallory", f"doc-{i}")
        ns.clock.advance(5)
    ns.svc.revoke("admin", "mallory")
    ns.clock.advance(10)
    ns.svc.get("mallory", "doc-2")  # stale ACL cache: still allowed (seeded weakness)
    ns.clock.advance(400)
    try:
        ns.svc.get("mallory", "doc-3")
    except PermissionError:
        pass
    clean = audit.detect(ns.audit.entries, ns.audit_pub)
    tampered = json.loads(json.dumps(ns.audit.entries))  # the attacker works on a copy of the stored log
    victim = rng.randrange(2, len(tampered) - 2)
    tampered[victim]["actor"] = "doc-service/bob"  # attacker blames bob
    del tampered[victim + 2]  # and deletes a later entry
    found = audit.detect(tampered, ns.audit_pub)
    rules = sorted({a["rule"] for a in clean})
    return {"milestone": "M3 signed, hash-chained audit log", "entries": len(ns.audit.entries), "clean_log_anomalies": rules,
            "tampered_at_seq": victim + 1, "tampered_log_findings": sorted({a["rule"] for a in found}),
            "pass": rules == ["access_after_revoke", "unwrap_burst"] and {"bad_signature", "seq_gap", "chain_break"} <= {a["rule"] for a in found}}, found


def m4_pq_sharing(ns) -> dict:
    kem = reg.POLICY["share_kem"]
    recipient = reg.new_recipient(kem)
    package = ns.svc.share("alice", "doc-1", recipient.public_key())
    opened = open_shared(package, recipient).startswith(b"contract")
    old = [a.id for a in reg.REGISTRY.values() if a.kind == "kem" and a.status == "deprecated"][0]
    try:
        reg.share_seal(old, recipient.public_key(), b"k" * 32, b"x")
        refused = False
    except reg.DisallowedAlgorithm:
        refused = True
    return {"milestone": "M4 PQ-hybrid sharing (HPKE)", "kem": kem, "pq": reg.REGISTRY[kem].pq, "recipient_opened": opened,
            "wrapped_dek_bytes": len(base64.b64decode(package["blob"])), f"new_share_with_{old}": "refused" if refused else "allowed",
            "pass": opened and refused and reg.REGISTRY[kem].pq}


def m5_fitness(ns) -> dict:
    ns.log.debug("upstream call", extra={"ctx": {"authorization": "Bearer " + "z" * 24, "pin": ns.pin.reveal()}})  # seeded leak attempt
    checks = {"agility_lint_violations": len(agility_lint.scan([HERE])),
              "key_export_calls": len(l19_fitness.key_export_calls([HERE])),
              "token_keys_exportable": len(l19_fitness.inventory(ns.token)),
              "threat_model_problems": len(solution_verified.check(solution_verified.load(HERE / "threat_model.json"))),
              "secrets_in_logs": len(scan_log(ns.log_stream.getvalue(), known=[ns.pin.reveal()]))}
    return {"milestone": "M5 fitness functions + threat model + secret handling", **checks, "pass": not any(checks.values())}


def m6_agent(anomalies, real=False) -> dict:
    rows = agent_explain.explain(anomalies, real=real)
    verdicts = {r["id"]: r["verdict"].split()[0] for r in rows}
    page = any(a["rule"] in ("bad_signature", "chain_break", "seq_gap") for a in anomalies)  # code decides the action
    return {"milestone": "M6 agent explains, code decides", "anomalies": len(anomalies),
            "accepted": sum(v == "ACCEPTED" for v in verdicts.values()), "rejected": [i for i, v in verdicts.items() if v == "REJECTED"],
            "action": "page on-call (integrity)" if page else "ticket", "pass": all(verdicts.get(a["id"]) for a in anomalies) and "A99" not in [i for i, v in verdicts.items() if v == "ACCEPTED"]}


def run(real=False) -> list:
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory(dir=HERE, ignore_cleanup_errors=True) as work:
        ns = service.start(Path(work))
        ns.work = Path(work)
        try:
            rows = [m1_envelope_rotation(ns, rng), m2_mtls(ns)]
            m3, anomalies = m3_audit(ns, rng)
            rows += [m3, m4_pq_sharing(ns), m5_fitness(ns), m6_agent(anomalies, real)]
        finally:
            service.stop(ns)
    return rows


if __name__ == "__main__":
    rows = run(real="--real" in sys.argv)
    for row in rows:
        print(json.dumps(row, sort_keys=False))
    print(json.dumps({"scorecard": "capstone", "passed": sum(r["pass"] for r in rows), "total": len(rows), "decided_by": "code"}))
