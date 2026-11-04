"""SLIs, SLOs and multiwindow burn-rate alerts from structured request logs (lesson 15 lab code).

Works for availability. Weakness (the failureLab): latency is only checked as an AVERAGE (mean <= 200 ms).
Run the demo: python app.py
"""
import bisect
import json
from datetime import datetime, timezone

PERIOD_DAYS = 30  # SLO period: error budget = (1 - SLO) x the requests in 30 days
# SLI = good events / valid events. name: (is the request valid for this SLI?, was it good?)
SLIS = {"availability": (lambda r: True, lambda r: r["status"] < 500)}
SLOS = {"availability": 0.999}
MEAN_LATENCY_LIMIT_MS = 200
# multiwindow, multi-burn-rate alerts (Google SRE Workbook, "Alerting on SLOs", table 5-8):
# (severity, long window s, short window s, burn-rate threshold); short window = 1/12 of the long one
ALERTS = [("page", 3600, 300, 14.4), ("page", 21600, 1800, 6.0), ("ticket", 259200, 21600, 1.0)]


def parse(lines):
    records = [json.loads(line) for line in lines if line.strip()]
    for r in records:
        r["t"] = datetime.strptime(r["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    return sorted(records, key=lambda r: r["t"])


def window(records, now, seconds):  # records are sorted by time: binary search for [now - seconds, now)
    def at(t):
        return bisect.bisect_left(records, t, key=lambda r: r["t"])
    return records[at(now - seconds):at(now)]


def bad_ratio(records, sli):
    is_valid, is_good = SLIS[sli]
    valid = [r for r in records if is_valid(r)]
    return sum(not is_good(r) for r in valid) / len(valid) if valid else 0.0


def burn_rate(records, sli, now, seconds):
    # burn rate 1 = spending the budget exactly over the SLO period; 14.4 = 2% of a 30-day budget in 1 hour
    return bad_ratio(window(records, now, seconds), sli) / (1 - SLOS[sli])


def budget_consumed(records, sli, now, days=3):
    """Share of the 30-day error budget spent in the last `days` (= burn rate x window / period)."""
    return burn_rate(records, sli, now, days * 86400) * days / PERIOD_DAYS


def label(seconds):
    return f"{seconds // 86400}d" if seconds >= 86400 else f"{seconds // 3600}h" if seconds >= 3600 else f"{seconds // 60}m"


def alerts(records, now):
    fired = []
    for sli in SLOS:
        for severity, long_s, short_s, threshold in ALERTS:
            burn_long, burn_short = burn_rate(records, sli, now, long_s), burn_rate(records, sli, now, short_s)
            if burn_long >= threshold and burn_short >= threshold:  # both: fires fast AND resets fast
                fired.append({"sli": sli, "severity": severity, "windows": f"{label(long_s)}/{label(short_s)}",
                              "burn_long": round(burn_long, 1), "burn_short": round(burn_short, 1),
                              "threshold": threshold})
    return fired


def percentile(values, p):  # nearest-rank: the value at or below which p% of the requests fall
    ordered = sorted(values)
    return ordered[max(0, -(-len(ordered) * p // 100) - 1)]


def latency_report(records, now, seconds=3600):
    ms = [r["ms"] for r in window(records, now, seconds)]
    return {"mean": round(sum(ms) / len(ms), 1), "p50": percentile(ms, 50), "p95": percentile(ms, 95),
            "p99": percentile(ms, 99), "requests": len(ms)}


def latency_problems(records, now):
    mean = latency_report(records, now)["mean"]  # weakness: a mean hides a slow tail
    return [] if mean <= MEAN_LATENCY_LIMIT_MS else [f"mean latency {mean} ms > {MEAN_LATENCY_LIMIT_MS} ms"]
