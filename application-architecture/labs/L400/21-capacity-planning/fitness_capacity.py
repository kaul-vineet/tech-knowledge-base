"""Fitness function (lesson 21): the capacity plan still meets the SLO with one instance down.

Run: python fitness_capacity.py [--solution]   (exit 1 = the plan breaks the SLO or the headroom)
Re-run it whenever the log, the growth numbers or the code's service time change.
"""
import json
import sys

import capacity
import l300_log
from app import HERE, load


def gate(cap):
    model = cap.load_model(l300_log.records())
    bench = cap.benchmark(model)
    n = cap.instances_needed(model, bench["capacity_rps"])
    one_down = cap.simulate(model["peak_rps"] / max(n - 1, 1), [ms for _, ms in model["requests"]])
    util = round(model["peak_rps"] / (max(n - 1, 1) * bench["capacity_rps"]), 2)  # at peak, one instance down
    ok = one_down["p99_ms"] <= cap.SLO_P99_MS and util <= cap.HEADROOM
    return {"gate": "capacity-n-plus-1", "ok": ok, "budget": f"p99 <= {cap.SLO_P99_MS} ms with one down, "
            f"peak <= {cap.HEADROOM:.0%} of capacity with one down", "value": {"instances": n, "p99_one_down_ms":
            one_down["p99_ms"], "peak_share_one_down": util}}


if __name__ == "__main__":
    module = load(HERE / "solution" / "capacity.py", "capacity_solution") if "--solution" in sys.argv else capacity
    result = gate(module)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)
