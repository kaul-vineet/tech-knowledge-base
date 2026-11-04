"""Try-it checks for lab 17. Run: python try_it.py   (numpy only, modelled time)"""
import backend
import orchestrator as lab
import solution_cache_key as sol


def compare(costs=None, classical_s=None):
    w = dict(lab.WORKLOAD, classical_s=classical_s or lab.WORKLOAD["classical_s"])
    old = backend.Costs
    if costs:
        backend.Costs = lambda: costs                       # swap the cost model the backend builds
    try:
        rows = {m: lab.run(m, key=sol.cache_key, w=w) for m in ("sync", "batched", "session")}
    finally:
        backend.Costs = old
    return {m: (r["wall_s"], r["billed_s"]) for m, r in rows.items()}


def busy_queue():
    """Try 1: a shared device with a 30 s queue per job. How far apart do the designs move?"""
    return compare(backend.Costs(queue_s=30.0))


def slow_classical_step():
    """Try 2: the classical update takes 70 s per iteration (> the 60 s interactive TTL of a session)."""
    return compare(classical_s=70.0)


if __name__ == "__main__":
    print("busy_queue (wall_s, billed_s)        ", busy_queue())
    print("slow_classical_step (wall_s, billed_s)", slow_classical_step())
