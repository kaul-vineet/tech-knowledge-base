"""Computes every number used in the worked examples of content/concepts/L300/*.md by running the labs.
Run from the domain folder:  python research/concept_examples_l300.py   (~3 s; lesson 15 uses real HTTP and real time)"""
import importlib, sys
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs" / "L300"


def load(lab, module):
    for name in ("helpers", "checker", "analyze", module):  # each lab has its own helpers.py
        sys.modules.pop(name, None)
    sys.path.insert(0, str(LABS / lab))
    try:
        return importlib.import_module(module)
    finally:
        sys.path.pop(0)


print("== 12 raft ==")
rf, sol = load("12-raft-replicated-log", "raft"), load("12-raft-replicated-log", "solution_raft")
s = rf.stale_leader_scenario()
print("without check:", len(s.checker.violations), "violations;", s.checker.violations[0])
s = sol.stale_leader_scenario(sol.Node)
print("with check:", [e for e in s.net.events if "denies" in e], "| leader log", [c for _, c in s.leader().log])
print("seeds 1-20 losing data without check:", sum(bool(rf.stale_leader_scenario(rf.Node, k).checker.violations) for k in range(1, 21)))

print("== 13 partitions ==")
pt = load("13-partitions-fault-injection", "partition")
from checker import check_register  # noqa: E402  (lab 13's checker, loaded above)
events, history, leaders = pt.run(pt.OPS, pt.FAULTS)
print("two-leader ticks:", [t for t, l in enumerate(leaders) if len(l) > 1], "| linearizable:", check_register(history)[0])
print("c1 write 3 ends at", [o["end"] for o in history if o["value"] == 3 and o["f"] == "write"][0], "| c2 read ->", history[-1]["value"])
sp = load("13-partitions-fault-injection", "solution_partition")
_, history, _ = sp.run(sp.OPS, sp.FAULTS)
print("fenced:", [o.get("error") for o in history if not o["ok"]], "| linearizable:", check_register(history)[0])

print("== 14 sagas ==")
sg, ss = load("14-sagas-compensation", "saga"), load("14-sagas-compensation", "solution_saga")
results, services, _, _ = sg.run_orders(fail_rate=0.3)
print("failed:", [k for k, v in results.items() if v != "completed"], "| audit:", sg.audit(*services))
_, services, log, _ = ss.run_orders(fail_rate=0.3)
print("solution o1 tail:", [(r["step"], r["status"]) for r in log.entries("o1")][-3:], "| audit:", ss.audit(*services) or "OK")

print("== 15 tracing (times vary) ==")
tr = load("15-distributed-tracing", "tracing")
from analyze import critical_path, traces  # noqa: E402
spans = tr.run_checkout()
root = min((x for x in spans if x["parent_id"] is None), key=lambda x: x["start"])
print("traces:", len(traces(spans)), "| path:", [(x["service"], x["name"], ms) for x, ms in critical_path(spans, root)])
st = load("15-distributed-tracing", "solution_tracing")
spans = st.run_checkout()
root = min((x for x in spans if x["parent_id"] is None), key=lambda x: x["start"])
print("fixed traces:", len(traces(spans)), "| path:", [(x["service"], x["name"], ms) for x, ms in critical_path(spans, root)])

print("== 16 backpressure ==")
bp, sb = load("16-backpressure-load-shedding", "backpressure"), load("16-backpressure-load-shedding", "solution_backpressure")
from helpers import simulate  # noqa: E402
for load_ in (0.8, 0.95):
    s = bp.summary(simulate(bp.Server(), [(20, load_ * bp.CAPACITY)], bp.SERVICE_MS))
    print(f"load {load_:.0%}: throughput {s['throughput_per_s']}/s, mean wait {s['mean_wait_ms']} ms, p99 {s['p99_ms']} ms")
recs = simulate(bp.Server(), bp.BURST, bp.SERVICE_MS)
print("unbounded burst:", bp.summary(recs), "| second 15:", bp.per_second(recs)[15])
print("bounded burst:", sb.summary(simulate(sb.Server(), sb.BURST, sb.SERVICE_MS)))
