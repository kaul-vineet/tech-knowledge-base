"""Computes every number used in the worked examples of content/concepts/*.md (and a few kept
for the lessons' checkYourself / misconceptions).
Run from the domain folder:  python research/concept_examples.py
"""
import hashlib, json, statistics, sys
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs" / "L100"

print("== 01 setup ==")
ports = list(range(8001, 8001 + 3))
body = json.dumps({"node": "node1", "port": 8001, "pid": 4242}).encode()
print("ports:", ports, "| health body:", body.decode(), "| Content-Length:", len(body))

print("== 02 two services ==")
body = json.dumps({"item": "pear", "price": 4}).encode()
print("response body:", body.decode(), "| Content-Length:", len(body))
lat = [10.0, 4.8, 4.7, 3.2, 3.0]  # ms, from the lab README run (re-run 2026-10-28 after the rebalance)
print("median ms:", statistics.median(lat), "| 3 sequential calls at median ms:", round(3 * statistics.median(lat), 1))

print("== 03 timeouts ==")
threads, rate = 10, 5  # worker threads in A, requests/s arriving
print("B hangs, no timeout: all threads busy after", threads / rate, "s")
print("timeout 0.5 s: max throughput while B hangs =", threads / 0.5, "req/s (>= 5 arriving)")
budget, spent = 2.0, 0.5
print("deadline budget left for downstream call:", budget - spent, "s")
sys.path.insert(0, str(LABS / "03-timeouts"))
import timeouts  # noqa: E402
print("lab p99.9 timeout:", timeouts.choose_timeout())

print("== 04 retries ==")
print("full-jitter ceilings s:", [min(0.5, 0.02 * 2 ** a) for a in range(6)])
p = 0.3
print("P(4 attempts all fail) =", round(p ** 4, 4))
print("expected attempts per request (max 4) =", round(sum(p ** k for k in range(4)), 3))
print("5 layers x 3 attempts each =", 3 ** 5, "calls at the bottom")
print("Envoy upper bounds ms for retries 1..3 (base 25):", [(2 ** n - 1) * 25 for n in (1, 2, 3)])

print("== 05 idempotency ==")
for amount in (10, 99):
    raw = json.dumps({"amount": amount}).encode()
    print(raw.decode(), "-> sha256", hashlib.sha256(raw).hexdigest()[:16], "...")
print("P(at least one of 5 responses lost, p=0.4) =", round(1 - 0.6 ** 5, 5))

print("== 06 lamport ==")
sys.path.insert(0, str(LABS / "06-lamport-clocks"))
import lamport  # noqa: E402
for lam, node, wall, text, _ in lamport.scenario():
    print(f"L={lam} {node} wall={wall:+.3f} {text}")
