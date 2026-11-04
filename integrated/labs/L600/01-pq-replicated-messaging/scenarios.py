"""Seeded scenarios shared by run_project.py and the tests: one function per milestone, seam and fitness function.
Each returns a dict of measured values plus "pass". `faults` is the set run_project.py --inject passes in."""
import json
import random

import group_crypto as gc
import pqmsg
from _kb import load
from harness import nonce_reuse, send

prob = load("prob", "prob_tools")
MEMBERS = ["alice", "bob", "carol"]


def _post_stuck(svc, sender, text, rng):
    """One post whose leader crashes right after the outbox write: the sealed row is stuck on that node's disk."""
    svc.chaos, svc.rng = 1.0, random.Random(0)
    status = send(svc, sender, text, rng, attempts=1)[0]
    svc.chaos = 0.0
    return status


def m1_welcome(faults=()):
    svc = pqmsg.Service(MEMBERS, seed=1, faults=faults)
    entry = svc.sync(svc.leader().name)["state"].epochs[-1]
    secrets = {m: d.fork().learn(entry) for m, d in svc.devices.items()}
    tampered = {**entry, "welcomes": {"alice": {**entry["welcomes"]["alice"]}}}
    tampered["welcomes"]["alice"]["kem_ct"] = gc.b64e(gc.b64d(entry["welcomes"]["alice"]["kem_ct"])[-32:])
    try:
        svc.devices["alice"].fork().learn(tampered)
        downgrade = "accepted"
    except gc.pq.HandshakeError:
        downgrade = "refused (HandshakeError)"
    r = {"milestone": "M1 hybrid X25519MLKEM768 welcomes", "members_with_same_epoch_secret": len(secrets),
         "distinct_secrets": len(set(secrets.values())), "key_package_B": len(svc.devices["alice"].key_package),
         "welcome_B": gc.welcome_bytes(entry["welcomes"]["alice"]), "epoch_entry_json_B": len(json.dumps(entry)),
         "downgraded_32B_share": downgrade}
    r["pass"] = r["distinct_secrets"] == 1 and r["key_package_B"] == 1216 and downgrade.startswith("refused")
    return r


def m2_replicated(faults=()):
    svc, rng = pqmsg.Service(MEMBERS, seed=2, faults=faults), random.Random(2)
    texts = [f"m2-{i}: launch plan v{i}" for i in range(30)]
    crashed = None
    for i, text in enumerate(texts):
        if i == 15:
            crashed = svc.leader().name
            svc.crash_leader()
        send(svc, MEMBERS[i % 3], text, rng)
    violations = svc.settle()
    nodes = svc.cluster.nodes.values()
    logs = [tuple(n.log[:n.commit]) for n in nodes]
    reads = {n.name: svc.replay("alice", n.name) for n in nodes}
    leaked = sum(t in cmd for n in nodes for _, cmd in n.log for t in texts)
    r = {"milestone": "M2 sealed envelopes on a 3-node Raft log", "messages": len(texts), "leader_crashed": crashed,
         "committed_per_replica": [len(x) for x in logs], "committed_logs_identical": len(set(logs)) == 1,
         "plaintext_in_any_log": leaked, "safety_violations": len(violations),
         "alice_reads_per_replica": {k: sum(t is not None for *_, t in v) for k, v in reads.items()}}
    r["pass"] = (r["committed_logs_identical"] and leaked == 0 and not violations
                 and all(v == [x for x in reads["n1"]] for v in reads.values()) and len(reads["n1"]) == 30)
    return r


def m3_api(faults=()):
    svc, rng = pqmsg.Service(MEMBERS, seed=3, faults=faults), random.Random(3)
    key = '"6f1c2a5e-0d4b-4c8e-9a71-3b2f8e5d4c10"'
    codes = {"no key": svc.post(None, "bob", "hi")[0], "first": svc.post(key, "bob", "hi")[0],
             "retry": svc.post(key, "bob", "hi")[0], "same key, new text": svc.post(key, "bob", "hello")[0]}
    stuck_rng = random.Random(33)
    first = _post_stuck(svc, "alice", "lunch at 12?", stuck_rng)
    retry = send(svc, "alice", "lunch at 12?", random.Random(33))  # same seeded key = the client's retry
    ikey = retry[1]["msg_id"]
    svc.settle()  # the crashed node restarts and relays its stuck row (at-least-once)
    leader = svc.cluster.nodes[svc.leader().name]
    in_log = sum(f'"ikey": "{ikey}"' in cmd for _, cmd in leader.log[:leader.commit])
    shown = [x for x in svc.replay("bob", leader.name) if x[0] == ikey]
    r = {"milestone": "M3 Idempotency-Key + transactional outbox", "status_codes": codes,
         "crash_after_outbox_write": first, "client_retry": retry[0], "sealed_ciphertexts_for_key": in_log,
         "messages_shown_for_key": len(shown)}
    r["pass"] = (codes == {"no key": 400, "first": 201, "retry": 200, "same key, new text": 422} and first == 503
                 and retry[0] == 201 and in_log == 2 and len(shown) == 1)
    return r


def m4_rotation(faults=()):
    svc, rng = pqmsg.Service(MEMBERS, seed=4, faults=faults), random.Random(4)
    for i in range(10):
        send(svc, MEMBERS[i % 3], f"epoch-1 message {i}", rng)
    late = _post_stuck(svc, "bob", "carol is out - new launch date 1 March", random.Random(44))  # client gives up
    svc.rotate(["alice", "bob"])  # remove carol: new epoch secret, welcomes only for alice, bob (and the sealer)
    for i in range(10):
        send(svc, ["alice", "bob"][i % 2], f"epoch-2 message {i}", rng)
    carol_send = send(svc, "carol", "am I still in?", rng)[0]
    svc.settle()
    reads = {(m, n): svc.replay(m, n) for m in MEMBERS for n in svc.cluster.nodes}
    leader = svc.sync(svc.leader().name)["state"]
    stale = [v for _, _, v in leader.rejected].count("stale_epoch")
    after_removal = [x for x in reads[("carol", "n1")] if x[2] is not None and "launch date" in x[2]]
    r = {"milestone": "M4 key rotation vs log replay", "epochs": leader.epoch, "late_epoch1_post": late,
         "stale_epoch_rejected": stale, "carol_send_after_removal": carol_send,
         "replay_from_index_1": {m: f"{sum(t is not None for *_, t in reads[(m, 'n2')])}/{len(reads[(m, 'n2')])}"
                                 for m in MEMBERS},
         "carol_reads_after_removal": len(after_removal),
         "replicas_agree": all(reads[(m, n)] == reads[(m, "n1")] for m in MEMBERS for n in svc.cluster.nodes)}
    r["pass"] = (r["replay_from_index_1"] == {"alice": "20/20", "bob": "20/20", "carol": "10/20"} and stale == 1
                 and not after_removal and carol_send == 409 and r["replicas_agree"])
    return r


def m5_contract(faults=()):
    svc, rng = pqmsg.Service(MEMBERS, seed=5, faults=faults, local_accept=None), random.Random(5)
    leader = svc.leader().name
    if "local-contract-config" in faults:  # rolling upgrade done by hand on ONE node's config
        svc.local_accept[leader] = [1, 2, 3]
        svc.rt[leader]["state"].local_accept = [1, 2, 3]
    st = svc.sync(leader)["state"]
    svc.control(gc.seal(svc.rt[leader]["sealer"].keys[1], 1, "alice", "legacy-0001", "pre-migration note", b"\x00" * 11 + b"\x01", 1))
    for i in range(2):
        send(svc, MEMBERS[i], f"v2 message {i}", rng)
    header = svc.wire[-1]["h"]
    renamed = {("nonce" if k == "n" else k): v for k, v in header.items()}
    svc.version = 3
    before_gate = send(svc, "bob", "v3 before gate", rng)[0]
    if "local-contract-config" not in faults:
        svc.control({"type": "contract", "accept": [1, 2, 3]})  # the gate: one log index flips every replica
    after_gate = send(svc, "carol", "v3 after gate", rng)[0]
    svc.settle()
    readable = {n: sum(t is not None for *_, t in svc.replay("alice", n)) for n in svc.cluster.nodes}
    try:
        gc.open_msg({1: b"k" * 32}, {"h": {"v": 9, "epoch": 1}, "ct": ""})
        unknown = "opened"
    except gc.EnvelopeError:
        unknown = "refused (EnvelopeError)"
    r = {"milestone": "M5 versioned envelope contract + crypto agility", "v2_contract_problems": gc.contract_problems(header, st.accept),
         "renamed_field_problems": gc.contract_problems(renamed, st.accept), "v3_before_gate": before_gate,
         "v3_after_gate": after_gate, "v3_aead": svc.wire[-1]["h"]["aead"], "readable_per_replica": readable,
         "unknown_version_9": unknown}
    r["pass"] = (r["v2_contract_problems"] == [] and r["renamed_field_problems"] == ["missing n"] and before_gate == 409
                 and after_gate == 201 and len(set(readable.values())) == 1 and readable[leader] == 4 and unknown.startswith("refused"))
    return r


def traffic(n, seed, faults=(), chaos=0.01, rotate_every=2500, nonce_factory=pqmsg.RandomNonce):
    """n messages from 3 senders with seeded leader crashes; returns the service and what the clients saw acked."""
    svc, rng, acked = pqmsg.Service(MEMBERS, seed=seed, faults=faults, chaos=chaos, nonce_factory=nonce_factory), random.Random(seed), {}
    for i in range(n):
        if i and i % rotate_every == 0:
            svc.rotate(MEMBERS)
        sender = MEMBERS[i % 3]
        status, body, _ = send(svc, sender, f"msg {i:05d} from {sender}: status green", rng)
        if status in (200, 201):
            acked[body["msg_id"]] = (sender, f"msg {i:05d} from {sender}: status green")
    return svc, acked


def keystream_demo(svc, acked):
    """Same key + same nonce: ct1 XOR ct2 = pt1 XOR pt2. Knowing pt1 (e.g. your own message) reveals pt2."""
    for hits in nonce_reuse(svc.wire).values():
        for idx in hits.values():
            a, b = svc.wire[idx[0]], svc.wire[idx[1]]
            if a["h"]["ikey"] in acked and b["h"]["ikey"] in acked and a["fp"] != b["fp"]:
                known = acked[a["h"]["ikey"]][1].encode()
                ca, cb = gc.b64d(a["ct"]), gc.b64d(b["ct"])
                n = min(len(known), len(cb) - 16)  # the last 16 bytes are the GCM tag
                out = bytes(x ^ y ^ z for x, y, z in zip(ca[:n], cb[:n], known[:n])).decode(errors="replace")
                return {"nonce": a["h"]["n"], "known_plaintext": known.decode(), "recovered": out,
                        "actual": acked[b["h"]["ikey"]][1]}
    return None


def seam_nonce_failover(faults=(), n=1500):
    svc, acked = traffic(n, seed=11, faults=faults, chaos=0.02)
    bad, _ = traffic(n, seed=11, faults={"leader-counter"}, chaos=0.02)
    reuse, bad_reuse = nonce_reuse(svc.wire), nonce_reuse(bad.wire)
    r = {"seam": "crypto <-> distributed: nonce uniqueness vs leader failover", "messages": n, "failovers": svc.failovers,
         "reused_nonces": sum(map(len, reuse.values())), "guard_proven_leader_counter_reuses": sum(map(len, bad_reuse.values()))}
    r["pass"] = r["reused_nonces"] == 0 and r["guard_proven_leader_counter_reuses"] > 0
    return r


def seam_rotation(faults=()):
    good, bad = m4_rotation(faults), m4_rotation({"accept-stale-epoch"})
    r = {"seam": "crypto <-> distributed: key rotation vs log replay", "stale_epoch_rejected": good["stale_epoch_rejected"],
         "carol_reads_after_removal": good["carol_reads_after_removal"],
         "guard_proven_accept_stale_epoch_carol_reads": bad["carol_reads_after_removal"]}
    r["pass"] = good["pass"] and bad["carol_reads_after_removal"] > 0
    return r


def seam_idempotency(faults=(), n=300):
    def dupes(f):
        svc, acked = traffic(n, seed=13, faults=f, chaos=0.05)
        svc.settle()
        shown = [x[0] for x in svc.replay("alice", "n1")]
        return len(svc.wire), len(shown) - len(set(shown)), len(set(shown)) == len(acked)
    wire, shown_dupes, complete = dupes(faults)
    _, bad_dupes, _ = dupes({"no-apply-dedupe"})
    r = {"seam": "application-architecture <-> distributed: idempotent retries vs duplicate ciphertexts", "messages": n,
         "ciphertexts_sealed": wire, "duplicates_shown": shown_dupes, "every_acked_shown_once": complete,
         "guard_proven_no_apply_dedupe_duplicates": bad_dupes}
    r["pass"] = wire > n and shown_dupes == 0 and complete and bad_dupes > 0
    return r


def seam_contract(faults=()):
    good, bad = m5_contract(faults), m5_contract({"local-contract-config"})
    r = {"seam": "application-architecture <-> crypto: envelope contract versioning across replicas",
         "readable_per_replica": good["readable_per_replica"], "guard_proven_local_config_readable": bad["readable_per_replica"]}
    r["pass"] = good["pass"] and len(set(bad["readable_per_replica"].values())) > 1
    return r


def fitness_traffic(faults=(), n=10000):
    """F1 + F2 from one run: 10k messages, ~1% leader crashes per post, rotation every 2,500 messages."""
    svc, acked = traffic(n, seed=7, faults=faults)
    violations = svc.settle()
    reads = [svc.replay("alice", name) for name in svc.cluster.nodes]
    reuse = sum(map(len, nonce_reuse(svc.wire).values()))
    f1 = {"fitness": "F1 no nonce reuse across 10k messages with random failovers", "messages": n,
          "failovers": svc.failovers, "ciphertexts_sealed": len(svc.wire), "reused_nonces": reuse,
          "birthday_bound_per_epoch": f"{prob.collision_upper(len(svc.wire) // 4 + 1, 2**96):.1e}", "pass": reuse == 0}
    f2 = {"fitness": "F2 all replicas decrypt identical plaintexts", "replicas": len(reads),
          "identical": all(r == reads[0] for r in reads), "shown": len(reads[0]), "acked": len(acked),
          "match_acked": {k: (s, t) for k, s, t in reads[0]} == acked, "safety_violations": len(violations)}
    f2["pass"] = f2["identical"] and f2["match_acked"] and f2["shown"] == len(acked) == n and not violations
    return f1, f2


def fitness_handshake(faults=()):
    svc = pqmsg.Service(MEMBERS, seed=8, faults=faults)
    w = svc.sync(svc.leader().name)["state"].epochs[-1]["welcomes"]["bob"]
    kp, wb = len(svc.devices["bob"].key_package), gc.welcome_bytes(w)
    return {"fitness": "F3 handshake size budget", "key_package_B": kp, "welcome_B": wb, "total_B": kp + wb,
            "budget": "welcome <= 1200 B, key package + welcome <= 2400 B", "pass": wb <= 1200 and kp + wb <= 2400}


def fitness_key_limit(faults=(), limit=5):
    saved, pqmsg.MAX_MSGS_PER_EPOCH = pqmsg.MAX_MSGS_PER_EPOCH, limit
    try:
        svc, rng = pqmsg.Service(MEMBERS, seed=9, faults=faults), random.Random(9)
        codes = [send(svc, "alice", f"limit {i}", rng)[0] for i in range(limit + 1)]
        svc.rotate(MEMBERS)
        after = send(svc, "alice", "after rotation", rng)[0]
    finally:
        pqmsg.MAX_MSGS_PER_EPOCH = saved
    return {"fitness": "F4 rotate before the random-nonce limit (2^32 messages per epoch key)", "limit_in_test": limit,
            "codes": codes, "after_rotation": after, "pass": codes == [201] * limit + [409] and after == 201}
