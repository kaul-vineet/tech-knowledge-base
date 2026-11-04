"""Seeded load test: 240 jobs (Poisson arrivals), client retries, a flaky-backend outage, slow chunks that outlive
their lease, and two recalibrations. Returns the numbers the scorecard and the fitness functions check."""
import random
import statistics

import backends as bk
import cachekeys
import results
from _kb import capacity, slo
from canon import canonicalise
from jobservice import Conflict, JobService
from ledger_loader import ledger_class

Q3 = 'OPENQASM 3.0;\ninclude "stdgates.inc";\n'
CIRCUITS = {   # family -> textual variants of ONE circuit (same canonical form)
    "bell": [Q3 + "qubit[2] q;\nh q[0];\ncx q[0], q[1];\n",
             'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg r[2];\ncreg c[2];\n// Bell pair\nh r[0];\ncx r[0],r[1];\nmeasure r -> c;\n',
             Q3 + "qubit[2] q;\nbit[2] c;\nx q[1]; x q[1];\nh q[0];  cx q[0], q[1];\nc = measure q;\n"],
    "ghz3": [Q3 + "qubit[3] q;\nh q[0];\ncx q[0], q[1];\ncx q[1], q[2];\n",
             Q3 + "qubit[3] g;\nh g[0]; h g[0]; h g[0];\ncx g[0], g[1];\ncx g[1], g[2];\n"],
    "pair+plus": [Q3 + "qubit[3] q;\nh q[0];\nh q[2];\ncx q[0], q[1];\n",
                  Q3 + "qubit[3] q;\nh q[2];\nh q[0];\ncx q[0], q[1];\n"],
    "ghz4": [Q3 + "qubit[4] q;\nh q[0];\ncx q[0], q[1];\ncx q[1], q[2];\ncx q[2], q[3];\n"],
}
BUDGET_P95_S = 30.0
RECALIBRATIONS = [(150.0, "slow-clean", {"p1": 0.001, "p2": 0.009, "damp": 0.003, "p01": 0.02, "p10": 0.025}),
                  (220.0, "fast-noisy", {"p1": 0.003, "p2": 0.03, "damp": 0.008, "p01": 0.025, "p10": 0.04})]
OUTAGE = (100.0, 140.0)                          # flaky-mid rejects every job start in this window


def workload(jobs=240, rate=0.8, seed=7):
    rng, t, reqs = random.Random(seed), 0.0, []
    families = list(CIRCUITS)
    for i in range(jobs):
        t += rng.expovariate(rate)
        fam = rng.choice(families)
        reqs.append((round(t, 3), {"job_id": f"j{i:03d}", "qasm": rng.choice(CIRCUITS[fam]), "shots": rng.choice((1000, 2000, 3000, 4000)),
                                   "seed": rng.randint(1, 8), "min_fidelity": rng.choice((0.75, 0.85))}))
        if rng.random() < 0.1:                   # client timed out and retried: same id, same body
            reqs.append((round(t + 0.5, 3), dict(reqs[-1][1])))
    return reqs


def run(fault=None, policy="floor+budget", jobs=240, rate=0.8, seed=7):
    fleet = bk.fleet(seed)
    fleet[2].outages.append(OUTAGE)
    svc = JobService(fleet, ledger_class(fault)(), key=cachekeys.FAULT_KEYS.get(fault, cachekeys.cache_key), policy=policy)
    reqs = workload(jobs, rate, seed)
    for t, req in reqs:
        svc.at(t, svc.submit, req)
    for t, name, cal in RECALIBRATIONS:
        svc.at(t, svc.backends[name].recalibrate, cal)
    svc.at(reqs[-1][0] + 1, _conflict_probe, svc, reqs[0][1])
    svc.run()
    return metrics(svc, reqs)


def _conflict_probe(svc, req):
    try:
        svc.submit({**req, "shots": req["shots"] + 1000})
        svc.conflict = "accepted"
    except Conflict as e:
        svc.conflict = str(e)


def metrics(svc, reqs):
    ids = sorted(svc.jobs)
    res = {j: svc.result(j) for j in ids}
    req = {j: svc.jobs[j]["req"] for j in ids}
    waits = [svc.jobs[j]["started"] - svc.jobs[j]["submitted"] for j in ids]
    hits = [svc.jobs[j]["cache_hit"] for j in ids if svc.jobs[j]["cache_hit"]]
    variant_hits = sum(svc.jobs[j]["cache_hit"] is not None and req[j]["qasm"] != svc.jobs[svc.jobs[j]["source"]]["req"]["qasm"]
                       for j in ids)
    commits = [e for e in svc.log if e.get("evt") == "commit"]
    fid = {j: svc.backends[svc.jobs[j]["backend"]].estimated_fidelity(svc.jobs[j]["n"], svc.jobs[j]["ops"]) for j in ids}
    inside = total = 0
    for j in ids:
        r, job = res[j], svc.jobs[j]
        exact = svc.backends[r["backend"]].exact_probs(job["n"], job["ops"], r["calibration_version"])
        for k, p in r["probs"].items():
            total += 1
            inside += abs(p - exact[int(k, 2)]) <= 1.96 * r["stderr"][k]
    done = max(svc.jobs[j]["done"] for j in ids)
    rate = len(ids) / reqs[-1][0]
    return {"jobs": len(ids), "submissions": len(reqs), "unique_ids": len({r["job_id"] for _, r in reqs}), "completed": sum(svc.jobs[j]["done"] is not None for j in ids),
            "shots_exact": sum(res[j]["shots"] == req[j]["shots"] for j in ids),
            "shots_requested": sum(req[j]["shots"] for j in ids), "shots_returned": sum(res[j]["shots"] for j in ids),
            "contract_violations": sum(bool(results.violations(res[j], req[j]["shots"])) for j in ids),
            "cache_hits": len(hits), "variant_hits": variant_hits, "cache_crossings": sum(h["cached_version"] != h["current_version"] for h in hits),
            "lease_expiries": sum(e.get("evt") == "lease-expired" for e in svc.log),
            "rejected_commits": sum(c["status"] != "accepted" for c in commits), "attempts": sum(svc.jobs[j]["attempts"] for j in ids),
            "breaker_opens": sum(e.get("evt") == "breaker" and e["to"] == "open" for e in svc.log),
            "restarts": sum(e.get("restarted", False) for e in svc.log),
            "max_in_flight": svc.max_busy, "slots": {n: b.slots for n, b in svc.backends.items()},
            "p50_queue_s": round(slo.percentile(waits, 50), 2), "p95_queue_s": round(slo.percentile(waits, 95), 2),
            "max_queue_s": round(max(waits), 2), "budget_p95_s": BUDGET_P95_S,
            "mean_est_fidelity": round(statistics.fmean(fid.values()), 4),
            "below_floor": sum(fid[j] < req[j]["min_fidelity"] for j in ids),
            "ci95_coverage": round(inside / total, 4), "makespan_s": round(done, 1),
            "littles_L_waiting": round(capacity.littles_law(rate, 1000 * statistics.fmean(waits)), 2),
            "per_backend": {n: sum(svc.jobs[j]["backend"] == n for j in ids) for n in svc.backends},
            "conflict": getattr(svc, "conflict", None)}


if __name__ == "__main__":
    import json
    print(json.dumps(run()))
