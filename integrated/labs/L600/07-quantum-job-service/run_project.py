"""L600 #07 scorecard: python run_project.py [--inject lease-expiry|stale-cache|text-key]

Prints one JSON line per milestone, seam and fitness function, then a summary; exits 1 if any line fails.
--inject reproduces a seeded fault: lease-expiry = the shipped unfixed ledger (the failure lab),
stale-cache = cache key without the calibration version, text-key = cache key from raw QASM text.
"""
import argparse
import json
import sys

import numpy as np

import backends as bk
import loadtest
import results
import scenarios
from _kb import dm, noise, sv
from canon import canonicalise, circuit_hash, to_sv

FAULTS = ("lease-expiry", "stale-cache", "text-key")


def canon_check():
    fams = {f: {circuit_hash(t) for t in texts} for f, texts in loadtest.CIRCUITS.items()}
    same_unitary = all(sv.equal_up_to_global_phase(sv.unitary(n, to_sv(ops)), sv.unitary(*_raw(t)))
                       for texts in loadtest.CIRCUITS.values() for t in texts for n, ops, _ in [canonicalise(t)])
    return {"families": len(fams), "one_hash_per_family": all(len(h) == 1 for h in fams.values()),
            "distinct_across_families": len(set().union(*fams.values())) == len(fams), "unitary_preserved": same_unitary}


def _raw(text):
    n, ops = canonicalise.__globals__["qasm"].parse(text)       # the L100 #5 reader, before canonicalisation
    return n, to_sv([(g, tuple(q)) for g, q in ops])


def backend_probe():
    """4000-shot Bell on fast-noisy: sampled vs exact noisy distribution, and mitigation vs the pre-readout state."""
    b = bk.fleet()[0]
    n, ops, _ = canonicalise(loadtest.CIRCUITS["bell"][0])
    counts = {}
    for c in range(4):
        for k, v in b.execute(n, ops, 1, 1000, 11, c).items():
            counts[k] = counts.get(k, 0) + v
    r = results.build("probe", counts, n, b.readout(n, 1), b.name, 1)
    exact = b.exact_probs(n, ops, 1)
    pre = dm.probabilities(dm.run(n, noise.noisy_steps(to_sv(ops), b.cal)))
    raw = np.array([r["probs"].get(dm.label(i, n), 0) for i in range(4)])
    mit = np.array([r["mitigated"][dm.label(i, n)] for i in range(4)])
    return {"tvd_sample_vs_exact": round(0.5 * float(np.abs(raw - exact).sum()), 4),
            "tvd_raw_vs_pre_readout": round(0.5 * float(np.abs(raw - pre).sum()), 4),
            "tvd_mitigated_vs_pre_readout": round(0.5 * float(np.abs(mit - pre).sum()), 4),
            "stderr_00_raw": r["stderr"]["00"], "stderr_00_mitigated": r["mitigated_stderr"]["00"]}


def collect(fault=None):
    return {"load": loadtest.run(fault=fault), "lab": scenarios.lease_expiry(fault), "drift": scenarios.drift_mid_job(),
            "partial": scenarios.partial_retry(), "canon": canon_check(), "probe": backend_probe()}


def lines(o):
    L, lab, cn, pr = o["load"], o["lab"], o["canon"], o["probe"]
    lab_view = {k: lab[k] for k in ("requested", "returned", "lease_expiries", "commits")}
    return [
        ("milestone", "M1 intake: canonicalise + idempotent submit", cn["one_hash_per_family"] and cn["distinct_across_families"]
         and L["submissions"] > L["jobs"] == L["unique_ids"] and L["conflict"] is not None,
         {**cn, "replayed_submissions": L["submissions"] - L["jobs"], "conflict": L["conflict"]}),
        ("milestone", "M2 noisy backends + scheduler", pr["tvd_sample_vs_exact"] <= 0.03 and L["below_floor"] == 0,
         {"tvd_sample_vs_exact": pr["tvd_sample_vs_exact"], "below_floor": L["below_floor"], "per_backend": L["per_backend"]}),
        ("milestone", "M3 reliable execution: retries, leases, breaker, bulkhead", L["completed"] == L["jobs"] and L["breaker_opens"] >= 1
         and all(L["max_in_flight"][n] <= L["slots"][n] for n in L["slots"]) and lab["returned"] == lab["requested"],
         {k: L[k] for k in ("completed", "attempts", "lease_expiries", "rejected_commits", "breaker_opens", "max_in_flight")}),
        ("milestone", "M4 results with error bars + readout mitigation", L["contract_violations"] == 0
         and pr["tvd_mitigated_vs_pre_readout"] < pr["tvd_raw_vs_pre_readout"] and pr["stderr_00_mitigated"] > pr["stderr_00_raw"],
         {**{k: pr[k] for k in pr if k != "tvd_sample_vs_exact"}, "contract_violations": L["contract_violations"]}),
        ("milestone", "M5 versioned result cache", L["cache_hits"] > 0 and L["variant_hits"] > 0 and L["cache_crossings"] == 0,
         {k: L[k] for k in ("cache_hits", "variant_hits", "cache_crossings")}),
        ("seam", "retries <-> shot accounting", lab["returned"] == lab["requested"] and o["partial"]["returned"] == 4000
         and L["shots_returned"] == L["shots_requested"], {**lab_view, "partial_retry_returned": o["partial"]["returned"],
                                                          "load_shots": [L["shots_returned"], L["shots_requested"]]}),
        ("seam", "canonicalisation <-> cache key", cn["unitary_preserved"] and cn["one_hash_per_family"] and L["variant_hits"] > 0,
         {"unitary_preserved": cn["unitary_preserved"], "variant_hits": L["variant_hits"]}),
        ("seam", "noise <-> result contract (uncertainty)", L["contract_violations"] == 0 and L["ci95_coverage"] >= 0.9,
         {"contract_violations": L["contract_violations"], "ci95_coverage": L["ci95_coverage"]}),
        ("seam", "calibration drift <-> cached results", L["cache_crossings"] == 0 and o["drift"]["restarts"] == 1
         and o["drift"]["calibration_version"] == 2 and o["drift"]["returned"] == 4000,
         {"cache_crossings": L["cache_crossings"], "mid_job_restarts": o["drift"]["restarts"],
          "drift_job_version": o["drift"]["calibration_version"], "load_restarts": L["restarts"]}),
        ("fitness", "shots returned == shots requested for 100% of jobs", L["shots_exact"] == L["jobs"],
         {"exact": L["shots_exact"], "jobs": L["jobs"], "threshold": "100%"}),
        ("fitness", "cache hit never crosses calibration versions", L["cache_crossings"] == 0,
         {"crossings": L["cache_crossings"], "hits": L["cache_hits"], "threshold": 0}),
        ("fitness", "p95 queue time under budget", L["p95_queue_s"] <= L["budget_p95_s"],
         {"p95_queue_s": L["p95_queue_s"], "p50_queue_s": L["p50_queue_s"], "budget_s": L["budget_p95_s"]}),
    ]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inject", choices=FAULTS)
    args = ap.parse_args(argv)
    rows = lines(collect(args.inject))
    for kind, name, ok, measure in rows:
        print(json.dumps({kind: name, "pass": bool(ok), "measure": measure}))
    tally = {k: f"{sum(bool(r[2]) for r in rows if r[0] == k)}/{sum(r[0] == k for r in rows)}" for k in ("milestone", "seam", "fitness")}
    print(json.dumps({"scorecard": tally, "fault": args.inject, "all_pass": all(r[2] for r in rows)}))
    return 0 if all(r[2] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
