"""Small, exact scenarios the seams and the failure lab are proved with (one job each, fake clock)."""
import backends as bk
from jobservice import JobService
from ledger_loader import ledger_class
from loadtest import CIRCUITS

CLEAN = {"p1": 0.0005, "p2": 0.005, "damp": 0.002, "p01": 0.01, "p10": 0.015}
DRIFTED = {"p1": 0.001, "p2": 0.009, "damp": 0.003, "p01": 0.02, "p10": 0.025}


def _one_job(backend, fault=None, shots=2000, events=()):
    svc = JobService([backend], ledger_class(fault)())
    req = {"job_id": "lab", "qasm": CIRCUITS["bell"][0], "shots": shots, "seed": 11, "min_fidelity": 0.0}
    svc.at(0.0, svc.submit, req)
    for t, fn in events:
        svc.at(t, fn)
    svc.run()
    r = svc.result("lab")
    return {"requested": shots, "returned": r["shots"], "attempts": svc.jobs["lab"]["attempts"],
            "lease_expiries": sum(e["evt"] == "lease-expired" for e in svc.log),
            "commits": [(e["chunk"], e["token"], e["status"]) for e in svc.log if e["evt"] == "commit"],
            "restarts": sum(e.get("restarted", False) for e in svc.log), "calibration_version": r["calibration_version"],
            "done_at": svc.jobs["lab"]["done"], "result": r}


def lease_expiry(fault=None):
    """Failure lab: the first two attempts run 15 s against a 10 s lease; free slots run the redeliveries (3 s)."""
    slow = bk.Backend("slow-clean", CLEAN, latency_s=3.0, slots=4, slow_starts=(1, 2), slow_factor=5.0)
    return _one_job(slow, fault)


def drift_mid_job():
    """Recalibration at t = 1 s: chunks 0-1 ran on v1, chunks 2-3 start on v2 -> the job restarts on v2."""
    b = bk.Backend("slow-clean", CLEAN, latency_s=3.0, slots=2)
    return _one_job(b, shots=4000, events=[(1.0, lambda: b.recalibrate(DRIFTED))])


def partial_retry():
    """Chunk starts fail transiently (seeded 50% rejections): only the failed chunks are retried."""
    b = bk.Backend("flaky-mid", CLEAN, latency_s=1.5, slots=3, fail_rate=0.5, seed=3)
    return _one_job(b, shots=4000)


if __name__ == "__main__":
    import json
    for name, fn in (("lease_expiry (fixed)", lease_expiry), ("lease_expiry (shipped ledger)", lambda: lease_expiry("lease-expiry")),
                     ("drift_mid_job", drift_mid_job), ("partial_retry", partial_retry)):
        out = fn()
        out.pop("result")
        print(name, json.dumps(out))
