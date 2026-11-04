"""Writes the capstone's 'real' data, seeded: data/history.csv (5 past days, one row per call: arrival time and
handle time; generated on demand, not committed), data/history_kpis.jsonl (the hourly service-level and
abandonment report for the same 5 days, simulated from the same hidden parameters) and data/today.jsonl (today's
live feed: one line per 15 minutes with the call count; demand surges +30% from 13:00).

The real centre is itself a simulation with hidden parameters - so the capstone can score itself honestly.
python make_data.py
"""
import csv
import json
from pathlib import Path

import numpy as np

import centre

DATA = Path(__file__).resolve().parent / "data"
TRUE_RATES = [2.0, 3.5, 5.0, 5.5, 4.5, 4.0, 4.5, 5.0, 4.0, 3.0, 2.5, 2.0]  # calls/min, 08:00 ... 19:00
TRUE_SERVICE, TRUE_CV, TRUE_PATIENCE = 4.0, 0.8, 3.0  # minutes; lognormal service; exponential patience
HISTORY_STAFF = [22] * 12  # what the centre staffed in the past: 22 agents all day
SURGE_FROM_H, SURGE = 5, 1.3  # today: +30% from 13:00 (hour index 5)


def history_day(day):
    """One past day, call by call (the same streams as centre.simulate, so it is reproducible)."""
    rng = np.random.default_rng([2026, day])
    calls = []
    for h, rate in enumerate(TRUE_RATES):
        n = rng.poisson(rate * 60)
        for t in np.sort(rng.uniform(60 * h, 60 * (h + 1), n)):
            calls.append({"day": day, "t_min": round(float(t), 3)})
    service = rng.lognormal(*centre.lognormal_params(TRUE_SERVICE, TRUE_CV), len(calls))
    for c, s in zip(calls, service):
        c["service_min"] = round(float(s), 3)  # handle time from the phone system (answered calls)
    hourly = centre.simulate(TRUE_RATES, HISTORY_STAFF, TRUE_SERVICE, TRUE_CV, TRUE_PATIENCE, seed=100 + day)
    return calls, hourly


def today_feed():
    rng = np.random.default_rng(2027)
    lines = []
    for q in range(48):  # 15-minute slots, 08:00-20:00
        h = q // 4
        rate = TRUE_RATES[h] * (SURGE if h >= SURGE_FROM_H else 1.0)
        lines.append({"slot": q, "t_min": 15 * q, "calls": int(rng.poisson(rate * 15))})
    return lines


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    rows, summary = [], []
    for day in range(1, 6):
        calls, hourly = history_day(day)
        rows += calls
        summary += [{"day": day, "hour": hour, **{k: round(v, 4) for k, v in m.items()}}
                    for hour, m in zip(range(centre.OPEN_H, centre.CLOSE_H), hourly)]
    with (DATA / "history.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["day", "t_min", "service_min"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (DATA / "history_kpis.jsonl").write_text("".join(json.dumps(r) + "\n" for r in summary), encoding="utf-8",
                                             newline="\n")
    (DATA / "today.jsonl").write_text("".join(json.dumps(r) + "\n" for r in today_feed()), encoding="utf-8", newline="\n")
    print(f"history: {len(rows)} calls over 5 days; kpis: {len(summary)} hour rows; today: 48 slots")
