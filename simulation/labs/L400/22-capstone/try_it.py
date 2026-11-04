"""tryIt for the capstone (run: python try_it.py): why the staffing rule uses 95% bounds, and Erlang C as a seed."""
import json

import numpy as np

import pipeline
import runner

inp = pipeline.model_inputs(pipeline.history())


def full_day(staff, reps=24):
    days = np.array([json.loads(runner.day_replication(((r,), inp["rates"], staff, inp["mean_service"], inp["cv"],
                                                         4.5))[1]) for r in range(reps)])
    return f"{sum(staff)} agent-hours, worst-hour mean abandonment {days[:, :, 1].mean(0).max():.3f}"


# 1. Decide each hour on POINT estimates (mean SL >= 0.80, mean abandonment <= 5%) instead of 95% bounds.
point = lambda rate: next(c for c in range(5, 60) if (lambda r: r["sl"] >= 0.80 and r["abandon"] <= 0.05)(
    pipeline.hour_check(rate, c, inp, 4.5)))
print("point estimates :", full_day([point(r) for r in inp["rates"]]))
print("95% bounds      :", full_day(pipeline.plan(inp["rates"], inp, 4.5)))
# 2. Erlang C alone (no abandonment, exponential service) - judged by the same simulation.
print("Erlang C only   :", full_day([pipeline.erlang_c_agents(r, inp["mean_service"]) for r in inp["rates"]]))
