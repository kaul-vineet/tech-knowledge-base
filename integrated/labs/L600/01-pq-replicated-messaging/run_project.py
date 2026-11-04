"""Project 01 scorecard: python run_project.py [--inject FAULT] [--messages N]
Prints one JSON line per milestone, seam and fitness function, then the scorecard; exits 1 if anything fails.
--inject reproduces a seam failure (leader-counter is the failure lab: nonce reuse after leader failover).
Seeded (SEED values live in scenarios.py); ciphertexts differ per run, every printed number does not."""
import argparse
import json
import sys

import pqmsg
import scenarios as sc


def failure_lab(n=1500):
    svc, acked = sc.traffic(n, seed=11, faults={"leader-counter"}, chaos=0.02)
    reuse = sc.nonce_reuse(svc.wire)
    first = sorted(int.from_bytes(bytes.fromhex(h), "big") for hits in reuse.values() for h in hits)[:5]
    return {"failure_lab": "leader-counter", "messages": n, "failovers": svc.failovers,
            "reused_nonces": sum(map(len, reuse.values())), "smallest_reused_nonce_values": first,
            "keystream_reuse": sc.keystream_demo(svc, acked)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inject", choices=pqmsg.FAULTS, help="seeded fault to reproduce")
    ap.add_argument("--messages", type=int, default=10000, help="messages in the F1/F2 traffic run")
    args = ap.parse_args(argv)
    faults = {args.inject} if args.inject else set()
    rows = [sc.m1_welcome(faults), sc.m2_replicated(faults), sc.m3_api(faults), sc.m4_rotation(faults),
            sc.m5_contract(faults), sc.seam_nonce_failover(faults), sc.seam_rotation(faults),
            sc.seam_idempotency(faults), sc.seam_contract(faults), *sc.fitness_traffic(faults, args.messages),
            sc.fitness_handshake(faults), sc.fitness_key_limit(faults)]
    for row in rows:
        print(json.dumps(row))
    if args.inject == "leader-counter":
        print(json.dumps(failure_lab()))
    passed = sum(r["pass"] for r in rows)
    print(json.dumps({"scorecard": "L600-01 pq-replicated-messaging", "injected": args.inject, "passed": passed,
                      "total": len(rows), "decided_by": "code"}))
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
