"""Every milestone, seam and fitness check as a function world -> (pass, detail). run_project.py prints them; the tests
call the same functions, so the scorecard and the test suite can never disagree."""
import json

import canonical as C
import client as CL
import mirrors as MR
import publisher as P
import science
import trust
from _kb import OPEN_DATA_SHIPPED, SIGNATURES, UNITS
from cryptography.hazmat.primitives.asymmetric import ed25519


def _try(fn):
    try:
        fn()
        return "ACCEPTED"
    except Exception as e:  # noqa: BLE001 - every refusal is reported with its reason
        return str(e)


def m1_process(w):
    cat = w.mirrors[0].objects["releases/v4/catalogue.json"]
    rows = json.loads(cat)["rows"]
    exact = all(r["distance_pc"] is None or r["distance_pc"] == UNITS.parallax_distance_pc(r["parallax_mas"] / 1000)
                for r in rows)
    ok = exact and cat == C.dumps(science.catalogue(4))  # re-running the step gives the same bytes
    return ok, {"rows": len(rows), "needs_prior": sum(r["method"] == "needs-prior" for r in rows),
                "first": f"{rows[0]['source_id']} {rows[0]['distance_pc']} pc"}


def m2_release(w):
    m = json.loads(w.mirrors[0].objects["releases/v4/release.json"])["signed"]
    return len(m["files"]) == 5, {"files": len(m["files"]), "merkle_root": m["merkle_root"][:16], "licence": m["licence"]}


def m3_signed(w):
    t1 = SIGNATURES.RFC8032_T1
    vector = ed25519.Ed25519PrivateKey.from_private_bytes(t1["secret"]).sign(b"") == t1["sig"]
    sigs = json.loads(w.mirrors[0].objects["releases/v4/release.json"])["signatures"]
    algs = [s["alg"] for s in sigs]
    return vector and algs == ["Ed25519", "ML-DSA-65"], {"rfc8032_t1": vector, "algs": algs,
                                                         "sig_bytes": [len(s["sig"]) // 2 for s in sigs],
                                                         "root_versions": len(w.pub.roots)}


def m4_replicated(w):
    conflicts = sorted(set().union(*[m.conflicts for m in w.mirrors]))
    ok = all(r["converged"] for r in w.rounds.values()) and not conflicts
    return ok, {"rounds": {v: r["rounds"] for v, r in w.rounds.items()}, "conflicts": conflicts[:3]}


def m5_client(w):
    c, ok, why = w.client(), [], {}
    for m in w.mirrors:
        r = _try(lambda: c.fetch(m, w.pub.log, w.now + 100))
        ok.append(m.name) if r == "ACCEPTED" else why.setdefault(m.name, r[:120])
    return len(ok) == 4, {"verified_from": ok, "log_size": len(w.pub.log.entries), **({"rejected": why} if why else {})}


def s1_canonical(w):
    cat = w.mirrors[0].objects["releases/v4/catalogue.json"]
    idempotent = C.dumps(json.loads(cat)) == cat
    same = len({m.objects.get("releases/v4/catalogue.json") for m in w.mirrors}) == 1
    return idempotent and same, {"jcs_bytes": len(cat), "platform_bytes": len(C.platform_dumps(json.loads(cat))),
                                 "mirrors_agree": same}


def s2_rotation(w):
    old = [v for v in (1, 2, 3, 4) if _try(lambda: CL.verify_release(w.mirrors[1].objects, v, w.root)) == "ACCEPTED"]
    m = json.loads(w.mirrors[1].objects["releases/v4/release.json"])["signed"]
    stolen = [trust.Signer("Ed25519", "demo-release-1"), trust.Signer("ML-DSA-65", "demo-release-1")]
    forged = dict(w.mirrors[1].objects, **{"releases/v5/release.json": C.dumps(trust.sign(dict(m, version=5), stolen))})
    v5 = _try(lambda: CL.verify_release(forged, 5, w.root))
    return old == [1, 2, 3, 4] and v5 != "ACCEPTED", {"old_releases_verify": old, "retired_key_signs_v5": v5[:80]}


def s3_freshness(w):
    c = w.client()
    c.fetch(w.mirrors[0], w.pub.log, w.now + 100)  # the client has now seen v4
    lag = _try(lambda: c.fetch(w.stale, w.pub.log, w.now + 100))
    expiry = json.loads(w.stale.timestamp)["signed"]["expires"]
    fz = w.client()  # a client that never saw v4: only the expiry protects it from a frozen mirror
    frozen = _try(lambda: fz.fetch(w.stale, w.pub.log, expiry + 1))
    return "ACCEPTED" not in (lag, frozen), {"lagging": lag[:90], "frozen": frozen[:90]}


def s4_licence(w):
    fn = OPEN_DATA_SHIPPED.release_licence if w.inject == "licence-drop" else P.OPEN_DATA.release_licence
    gate = _try(lambda: P.build_files(5, licence_fn=fn))
    stripped = dict(w.mirrors[1].objects, **{"releases/v4/ACKNOWLEDGEMENTS.md": b"Data: ESA Gaia.\n"})
    strip = _try(lambda: CL.verify_release(stripped, 4, w.root))
    lic = w.mirrors[1].objects["releases/v4/LICENSE.txt"].decode().strip()
    return gate == "ACCEPTED" and strip != "ACCEPTED", {"licence": lic, "gate": "signed" if gate == "ACCEPTED" else
                                                         gate[:100], "stripped_mirror": strip}


def f1_tamper(w, version=4):
    """Flip one bit in every byte of every object of release v4; verification must refuse each one."""
    objs, caught, total = w.mirrors[0].objects, 0, 0
    for key in [k for k in objs if k.startswith(f"releases/v{version}/")]:
        good = objs[key]
        for i in range(len(good)):
            bad = dict(objs, **{key: good[:i] + bytes([good[i] ^ 0x01]) + good[i + 1:]})
            total += 1
            caught += _try(lambda: CL.verify_release(bad, version, w.root)) != "ACCEPTED"
    return caught == total, {"caught": caught, "total": total, "rate": round(caught / total, 6)}


def f2_convergence(w, seeds=range(1, 101), bound=4):
    """Fresh 4-mirror cluster, v4 uploaded to m0 only; 100 gossip seeds, with and without m3 down for the first 3
    rounds. Measured: rounds after the last mirror became reachable until every root and timestamp agree."""
    worst = {}
    for label, down in (("all_up", {}), ("m3_down_3", {"m3": 3})):
        rs = []
        for s in seeds:
            ms = [MR.Mirror(f"m{i}") for i in range(4)]
            for k, raw in w.objects.items():
                ms[0].put(k, raw)
            ms[0].put_timestamp(w.ts)
            st = MR.gossip(ms, seed=s, down_until=down)
            rs.append(st["rounds"] - max(down.values(), default=0) if st["converged"] else 99)
        worst[label] = max(rs)
        worst[label + "_mean"] = round(sum(rs) / len(rs), 2)
    return max(worst["all_up"], worst["m3_down_3"]) <= bound, {"bound": bound, **worst}


def f3_rollback(w):
    c = w.client()
    c.fetch(w.mirrors[0], w.pub.log, w.now + 100)
    rejected = [v for v in (1, 2, 3) if _try(lambda: c.fetch(_offering(w, v), w.pub.log, w.now + 100)) != "ACCEPTED"]
    return rejected == [1, 2, 3], {"older_versions_rejected": rejected}


def _offering(w, v):
    """A mirror whose (validly signed, unexpired) timestamp names old release v: replay of an old timestamp."""
    m = MR.Mirror(f"replay-v{v}")
    m.objects = dict(w.mirrors[1].objects)
    old = dict(json.loads(w.ts)["signed"], release={"version": v, "sha256": P.sha(m.objects[f"releases/v{v}/release.json"])})
    m.timestamp = C.dumps(trust.sign(dict(old, version=v), [w.pub.ts_key]))
    return m


CHECKS = [("milestone", "M1", "process: parallax -> distance on the L400 #21 rows", m1_process),
          ("milestone", "M2", "content-addressed release with a Merkle manifest", m2_release),
          ("milestone", "M3", "dual-signed (Ed25519 + ML-DSA-65) with a root key rotation", m3_signed),
          ("milestone", "M4", "replicated to 4 mirrors by anti-entropy", m4_replicated),
          ("milestone", "M5", "client verifies signatures, hashes and log proofs", m5_client),
          ("seam", "S1", "astronomy floats <-> SHA-256: canonical encoding (RFC 8785)", s1_canonical),
          ("seam", "S2", "key rotation <-> verifying old releases", s2_rotation),
          ("seam", "S3", "mirror lag <-> client freshness (rollback / freeze)", s3_freshness),
          ("seam", "S4", "licence + attribution <-> the signed release", s4_licence),
          ("fitness", "F1", "any single-byte tamper is detected", f1_tamper),
          ("fitness", "F2", "mirrors converge within 4 gossip rounds", f2_convergence),
          ("fitness", "F3", "client rejects a release older than the newest seen", f3_rollback)]
