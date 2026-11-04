"""tryIt for lesson 12 (uses the fixed planner in solution/plan.py).
1. Same night, second site: Sydney (33.87 S, 151.21 E, AEDT = UTC+11).
2. Tighten the Moon rule from 30 to 45 degrees on the Gurgaon night.
"""
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("plan_fixed", HERE / "solution" / "plan.py")
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)


def names(rows):
    return [f"{r['target']}@{r['start']}" for r in rows]


if __name__ == "__main__":
    sydney = {"name": "Sydney", "lat": -33.87, "lon": 151.21, "tz": timezone(timedelta(hours=11))}
    start = datetime(2026, 11, 24, 19, 0, tzinfo=sydney["tz"])
    rows, left = plan.schedule(sydney, start)
    print("1. Sydney dark", "-".join(plan.dark_window(sydney, start)), "| scheduled", names(rows), "| unscheduled", left)
    plan.MIN_MOON_SEP = 45.0
    rows, left = plan.schedule()
    print("2. Gurgaon, Moon >= 45 deg | scheduled", names(rows), "| unscheduled", left)
