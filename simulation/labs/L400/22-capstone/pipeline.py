"""Capstone milestones 1-4: input modelling, calibration + holdout validation, sensitivity, staffing optimisation.

Reuses: L200 lesson 7 (fit_inputs: candidate fits + KS distance) and L200 lesson 8 (mmc_queue.erlang_c).
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

import centre
import make_data

HERE = Path(__file__).resolve().parent
for lab in ("07-input-modelling", "08-multi-server-queue"):
    sys.path.append(str(HERE.parents[1] / "L200" / lab))
import fit_inputs  # noqa: E402
import mmc_queue  # noqa: E402

FIT_DAYS, HOLDOUT_DAYS = (1, 2, 3), (4, 5)  # calibrate on the first three days, validate on the last two
SL_TARGET, ABANDON_MAX, REPS = 0.80, 0.05, 10
T_975 = {9: 2.262, 19: 2.093}  # Student t, two-sided 95%


def history():
    path = make_data.DATA / "history.csv"
    if not path.exists():  # the call log is generated on demand (seeded) and not committed
        import subprocess
        subprocess.run([sys.executable, str(HERE / "make_data.py")], check=True, cwd=HERE)
    with path.open(encoding="utf-8", newline="") as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]


def kpis():
    return [json.loads(line) for line in (make_data.DATA / "history_kpis.jsonl").read_text(encoding="utf-8").splitlines()]


def model_inputs(calls):
    """M1: hourly arrival rates (calls/min) and the service-time distribution, from the fit days only."""
    fit = [c for c in calls if c["day"] in FIT_DAYS]
    counts = np.bincount([int(c["t_min"] // 60) for c in fit], minlength=12)[:12]
    rates = (counts / (len(FIT_DAYS) * 60)).round(3).tolist()
    x = np.array([c["service_min"] for c in fit])
    fits = sorted(((fit_inputs.ks_statistic(x, f["cdf"]), f) for f in (g(x) for g in fit_inputs.FITTERS)),
                  key=lambda p: p[0])
    d, best = fits[0]
    return {"rates": rates, "service_dist": best["name"], "ks_d": round(d, 4),
            "ks_all": {f["name"]: round(dd, 4) for dd, f in fits},
            "mean_service": round(float(x.mean()), 3), "cv": round(float(x.std() / x.mean()), 3)}


def day_kpis(inp, patience, staff, reps=REPS, seed0=0):
    runs = [centre.simulate(inp["rates"], staff, inp["mean_service"], inp["cv"], patience, seed=seed0 + r)
            for r in range(reps)]
    return {k: np.mean([[h[k] for h in run] for run in runs], axis=0) for k in ("sl", "abandon")}


def observed(days):
    rows = [r for r in kpis() if r["day"] in days]
    return {k: np.mean([[r[k] for r in rows if r["day"] == d] for d in days], axis=0) for k in ("sl", "abandon")}


def calibrate(inp, grid=np.arange(1.0, 6.01, 0.5)):
    """M3: the one input the data cannot show directly - patience - fitted to the observed abandonment profile."""
    target = observed(FIT_DAYS)["abandon"]
    sse = {float(p): float(((day_kpis(inp, p, make_data.HISTORY_STAFF, reps=5)["abandon"] - target) ** 2).sum())
           for p in grid}  # same seeds for every candidate: common random numbers
    return min(sse, key=sse.get), sse


def validate(inp, patience):
    """M3: holdout validation on days the calibration never saw (percentage-point errors per hour)."""
    sim, obs = day_kpis(inp, patience, make_data.HISTORY_STAFF, seed0=500), observed(HOLDOUT_DAYS)
    return {f"{k}_mae_pp": round(float(np.mean(np.abs(sim[k] - obs[k]))) * 100, 2) for k in ("sl", "abandon")}


def hour_check(rate, agents, inp, patience, reps=REPS):
    runs = [centre.period(rate, agents, inp["mean_service"], inp["cv"], patience, seed=r) for r in range(reps)]
    sl, ab = np.array([r["sl"] for r in runs]), np.array([r["abandon"] for r in runs])
    t = T_975[reps - 1] / math.sqrt(reps)
    low, high = sl.mean() - t * sl.std(ddof=1), ab.mean() + t * ab.std(ddof=1)  # 95% bounds, not point estimates
    return {"agents": agents, "sl": float(sl.mean()), "sl_low": float(low), "abandon": float(ab.mean()),
            "abandon_high": float(high), "ok": bool(low >= SL_TARGET and high <= ABANDON_MAX)}


def erlang_c_agents(rate, mean_service):
    """Erlang C staffing (no abandonment, exponential service): smallest c with P(wait <= 1 min) >= target."""
    c = math.floor(rate * mean_service) + 1
    while True:
        r = mmc_queue.erlang_c(c, rate, 1 / mean_service)
        if 1 - r["P_wait"] * math.exp(-(c / mean_service - rate) * centre.SL_MIN) >= SL_TARGET:
            return c
        c += 1


def plan_hour(rate, inp, patience):
    """M4: start at Erlang C, then let the simulation (abandonment, real service variability) move c."""
    c = erlang_c_agents(rate, inp["mean_service"])
    check = hour_check(rate, c, inp, patience)
    while not check["ok"]:
        c += 1
        check = hour_check(rate, c, inp, patience)
    while c > 1 and (lower := hour_check(rate, c - 1, inp, patience))["ok"]:
        c, check = c - 1, lower
    return check


def plan(rates, inp, patience, rounds=6):
    """Hour-by-hour plan, then repaired against the FULL day (queues carry over between hours)."""
    staff = [plan_hour(rate, inp, patience)["agents"] for rate in rates]
    for _ in range(rounds):
        day = day_kpis(dict(inp, rates=rates), patience, staff, seed0=900)
        short = [h for h in range(len(rates)) if day["sl"][h] < SL_TARGET or day["abandon"][h] > ABANDON_MAX]
        if not short:
            break
        staff = [c + (h in short) for h, c in enumerate(staff)]  # one more agent where the day still misses
    return staff


def sensitivity(inp, patience, staff, hour=3, h=0.1, reps=20):
    """Elasticity of the peak-hour service level to +/-10% in each input (common random numbers)."""
    base = dict(rate=inp["rates"][hour], mean_service=inp["mean_service"], patience=patience)
    sl = lambda **kw: np.mean([centre.period(kw["rate"], staff[hour], kw["mean_service"], inp["cv"], kw["patience"],
                                             seed=r)["sl"] for r in range(reps)])
    out = {}
    for name in base:
        up, down = dict(base, **{name: base[name] * (1 + h)}), dict(base, **{name: base[name] * (1 - h)})
        out[name] = round(float((sl(**up) - sl(**down)) / (2 * h) / sl(**base)), 2)
    return out
