"""Recompute every number in L600 #07 (lesson, concept note, ADRs, README) and its question bank.

Run from anywhere: python integrated/research/checks_07.py   -> prints OK and exits 0, or lists mismatches and exits 1.
Calculation answers are recomputed here; code-reading snippets are executed from the lab folder.
"""
import contextlib
import io
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]                     # kb/integrated
LAB = ROOT / "labs" / "L600" / "07-quantum-job-service"
sys.path.insert(0, str(LAB))
os.environ.pop("BUILD_TARGET", None)

import backends as bk  # noqa: E402
import jobservice  # noqa: E402
import loadtest  # noqa: E402
import run_project  # noqa: E402
import scenarios  # noqa: E402
from canon import canonicalise  # noqa: E402
from jobservice import JobService  # noqa: E402
from ledger_loader import ledger_class  # noqa: E402

errors = []


def eq(name, got, want, tol=0.0):
    ok = abs(got - want) <= tol if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    if not ok:
        errors.append(f"{name}: got {got!r}, want {want!r}")


# ---------- the load test and its faults ----------
base = loadtest.run()
lease_fault = loadtest.run(fault="lease-expiry")
stale = loadtest.run(fault="stale-cache")
text = loadtest.run(fault="text-key")
best = loadtest.run(policy="best-fidelity")
fast = loadtest.run(policy="fastest")
jobservice.LEASE_S = 20.0
long_lease = loadtest.run()
jobservice.LEASE_S = 10.0

for k, v in {"jobs": 240, "completed": 240, "shots_exact": 240, "shots_requested": 590000, "shots_returned": 590000,
             "contract_violations": 0, "cache_hits": 108, "variant_hits": 46, "cache_crossings": 0, "lease_expiries": 15,
             "rejected_commits": 2, "attempts": 405, "breaker_opens": 4, "p95_queue_s": 18.38, "p50_queue_s": 0.0,
             "max_queue_s": 38.5, "below_floor": 0, "mean_est_fidelity": 0.8852, "ci95_coverage": 0.9362, "restarts": 1,
             "per_backend": {"fast-noisy": 6, "slow-clean": 70, "flaky-mid": 164},
             "max_in_flight": {"fast-noisy": 4, "slow-clean": 2, "flaky-mid": 3}}.items():
    eq(f"base.{k}", base[k], v)
eq("replays", base["submissions"] - base["jobs"], 29)
eq("lease.shots_returned", lease_fault["shots_returned"], 604000)
eq("lease.shots_exact", lease_fault["shots_exact"], 226)
eq("lease.jobs_over", lease_fault["jobs"] - lease_fault["shots_exact"], 14)
eq("lease.contract_violations", lease_fault["contract_violations"], 14)
eq("lease.extra_per_job", (lease_fault["shots_returned"] - lease_fault["shots_requested"]) / 14, 1000)
eq("stale.hits", stale["cache_hits"], 128)
eq("stale.crossings", stale["cache_crossings"], 28)
eq("stale.variant_hits", stale["variant_hits"], 53)
eq("text.hits", text["cache_hits"], 70)
eq("text.variant_hits", text["variant_hits"], 0)
eq("text.lost_hits", base["cache_hits"] - text["cache_hits"], 38)
eq("best.p95", best["p95_queue_s"], 1163.38)
eq("best.fid", best["mean_est_fidelity"], 0.9078)
eq("best.per_backend", best["per_backend"]["slow-clean"], 240)
eq("fast.p95", fast["p95_queue_s"], 0.0)
eq("fast.fid", fast["mean_est_fidelity"], 0.8522)
eq("fast.below_floor", fast["below_floor"], 46)
eq("fid.gap_best_vs_chosen", round(best["mean_est_fidelity"] - base["mean_est_fidelity"], 4), 0.0226)
eq("lease20.expiries", long_lease["lease_expiries"], 0)
eq("lease20.rejected", long_lease["rejected_commits"], 0)
eq("lease20.attempts", long_lease["attempts"], 400)
eq("lease20.p95", long_lease["p95_queue_s"], 15.55)
eq("lease20.exact", long_lease["shots_exact"], 240)
eq("hit_share", round(100 * base["cache_hits"] / base["jobs"]), 45)

# ---------- exact scenarios ----------
fixed, shipped = scenarios.lease_expiry(), scenarios.lease_expiry("lease-expiry")
eq("lab.fixed", (fixed["requested"], fixed["returned"], fixed["lease_expiries"]), (2000, 2000, 2))
eq("lab.fixed.commits", fixed["commits"], [(0, 3, "accepted"), (1, 4, "accepted"), (0, 1, "REJECTED (token 1 < 3)"),
                                           (1, 2, "REJECTED (token 2 < 4)")])
eq("lab.shipped.returned", shipped["returned"], 4000)
drift = scenarios.drift_mid_job()
eq("drift", (drift["restarts"], drift["calibration_version"], drift["returned"]), (1, 2, 4000))
partial = scenarios.partial_retry()
eq("partial", (partial["returned"], len(partial["commits"])), (4000, 4))

# ---------- probe: sampling, mitigation, error bars ----------
probe = run_project.backend_probe()
for k, v in {"tvd_sample_vs_exact": 0.0088, "tvd_raw_vs_pre_readout": 0.0653, "tvd_mitigated_vs_pre_readout": 0.0098,
             "stderr_00_raw": 0.007898, "stderr_00_mitigated": 0.008486}.items():
    eq(f"probe.{k}", probe[k], v)
cn = run_project.canon_check()
eq("canon", (cn["families"], cn["one_hash_per_family"], cn["distinct_across_families"], cn["unitary_preserved"]),
   (4, True, True, True))

# ---------- Wald vs Wilson coverage over every outcome of executed jobs ----------
fleet = bk.fleet(7)
fleet[2].outages.append(loadtest.OUTAGE)
svc = JobService(fleet, ledger_class()())
for t, r in loadtest.workload():
    svc.at(t, svc.submit, r)
for t, n, c in loadtest.RECALIBRATIONS:
    svc.at(t, svc.backends[n].recalibrate, c)
svc.run()
wald = [0, 0]
wilson = [0, 0]
for j, job in svc.jobs.items():
    if job["cache_hit"]:
        continue
    r = svc.result(j)
    N = r["shots"]
    exact = svc.backends[r["backend"]].exact_probs(job["n"], job["ops"], r["calibration_version"])
    for i, e in enumerate(exact):
        if e >= 0.01:
            continue
        p = r["counts"].get(format(i, f"0{job['n']}b"), 0) / N
        z = 1.96
        wald[1] += 1
        wald[0] += abs(p - e) <= z * math.sqrt(p * (1 - p) / N)
        den = 1 + z * z / N
        centre, half = (p + z * z / (2 * N)) / den, z * math.sqrt(p * (1 - p) / N + z * z / (4 * N * N)) / den
        wilson[1] += 1
        wilson[0] += abs(e - centre) <= half
eq("wald.rare", round(wald[0] / wald[1], 4), 0.8216)
eq("wilson.rare", round(wilson[0] / wilson[1], 4), 0.9561)
eq("rare.count", wald[1], 342)

# ---------- static values used in the text ----------
slow = bk.fleet()[1]
eq("slow.expected_latency", round(slow.expected_latency(), 3), 4.898)
fl = bk.fleet()
n, ops, _ = canonicalise(loadtest.CIRCUITS["ghz4"][0])
eq("ghz4.fast_fid", round(fl[0].estimated_fidelity(n, ops), 4), 0.6976)

# ---------- every key number appears where the lesson says it does ----------
lesson_text = (ROOT / "content" / "parts" / "07.json").read_text(encoding="utf-8")
note = (ROOT / "content" / "concepts" / "L600" / "07-quantum-job-service.md").read_text(encoding="utf-8")
adrs = "".join(p.read_text(encoding="utf-8") for p in sorted((LAB / "decisions").glob("*.md")))
readme = (LAB / "README.md").read_text(encoding="utf-8")
for s in ["590,000", "604,000", "18.38", "1163.38", "0.8852", "0.9078", "0.8522", "0.0653", "0.0098", "0.007898",
          "0.008486", "0.9362", "15.55", "38.5", "82.16", "0.0088", "\"exact 226 of 240", "28 of 128"]:
    if s.strip('"') not in lesson_text:
        errors.append(f"lesson text lacks {s}")
for s in ["590,000", "18.38", "0.0653", "0.0098", "0.007898", "0.008486", "93.62", "82.16", "95.61", "604,000", "38.5"]:
    if s not in note:
        errors.append(f"concept note lacks {s}")
for s in ["604,000", "1163.38", "0.9078", "0.8852", "0.8522", "18.38", "38.5", "128", "53", "46", "108", "70", "0.0226"]:
    if s not in adrs:
        errors.append(f"ADRs lack {s}")
if '"ci95_coverage": 0.9362' not in readme or '"tvd_sample_vs_exact": 0.0088' not in readme:
    errors.append("README scorecard output is stale")

# ---------- question bank ----------
qs = json.loads((ROOT / "content" / "qbank" / "parts" / "07.json").read_text(encoding="utf-8"))
byid = {q["id"]: q for q in qs}
CALC = {
    "int07-L600-009": f"{math.sqrt(3000 / 4000):.2f}",
    "int07-L600-010": f"{math.sqrt(0.25 / 4000):.4f}",
    "int07-L600-011": f"{3.0 * (1 + 0.15 * 4) / 0.98:.2f} s",
    "int07-L600-012": f"{(4 + 2 + 1) / 2 * slow.expected_latency():.2f} s - above the target, so it is skipped",
    "int07-L600-014": "3 chunks: 1000, 1000 and 500 shots" if -(-2500 // 1000) == 3 and 2500 - 2 * 1000 == 500 else "?",
    "int07-L600-015": f"{0.8 * 5:g}",
    "int07-L600-016": f"{(1 - 0.03) ** 2:.4f}",
}
b = bk.Backend("x", {"p1": 0.004, "p2": 0.04, "damp": 0.01, "p01": 0.03, "p10": 0.05}, latency_s=1, slots=1)
nb, opsb, _ = canonicalise(loadtest.CIRCUITS["bell"][0])
CALC["int07-L600-013"] = f"{b.estimated_fidelity(nb, opsb):.3f}"
eq("bell_fid_manual", round(0.996 * 0.96 * 0.99 ** 3 * 0.96 ** 2, 3), float(CALC["int07-L600-013"]))
eq("wait_without_backoff", round(6 / 2 * slow.expected_latency(), 2), 14.69)
eq("stderr_inverse", round(math.sqrt(4000 / 3000), 3), 1.155)
for qid, want in CALC.items():
    q = byid[qid]
    if q["type"] != "calculation" or q["options"][q["answer"]] != want:
        errors.append(f"{qid}: answer {q['options'][q['answer']]!r} != recomputed {want!r}")

cwd = os.getcwd()
os.chdir(LAB)
try:
    for q in qs:
        if q["type"] != "code-reading":
            continue
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(q["code"], q["id"], "exec"), {"__name__": "__qbank__"})
        last = buf.getvalue().strip().splitlines()[-1]
        if q["options"][q["answer"]] != last:
            errors.append(f"{q['id']}: answer {q['options'][q['answer']]!r} != printed {last!r}")
finally:
    os.chdir(cwd)

types = Counter(q["type"] for q in qs)
pos = Counter(q["answer"] for q in qs)
eq("qbank.count>=30", len(qs) >= 30, True)
eq("qbank.calc>=5", types["calculation"] >= 5, True)
eq("qbank.debug>=5", types["debugging"] >= 5, True)
eq("qbank.code>=4", types["code-reading"] >= 4, True)
eq("qbank.seams>=6", sum(1 for q in qs if q["source"].startswith("Lesson 7 (L600) seams") or "seam" in q["question"].lower()
                         or q["id"] in {f"int07-L600-{i:03d}" for i in range(1, 9)}) >= 6, True)
for q in qs:
    if len(q["options"]) != 4 or len(set(q["options"])) != 4 or not 0 <= q["answer"] <= 3 or q["level"] != "L600" \
            or q["lesson"] != 7 or len(q["explanation"]) < 30:
        errors.append(f"{q['id']}: malformed")
for a in range(4):
    if not 0.2 <= pos[a] / len(qs) <= 0.3:
        errors.append(f"answer {'ABCD'[a]} share {pos[a] / len(qs):.0%}")
longest = sum(max(range(4), key=lambda k: len(q["options"][k])) == q["answer"] for q in qs)
eq("qbank.longest<=45%", longest / len(qs) <= 0.45, True)

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK - lesson, note, ADRs, README and {len(qs)} questions recomputed "
      f"(types {dict(types)}, answers {dict(sorted(pos.items()))})")
