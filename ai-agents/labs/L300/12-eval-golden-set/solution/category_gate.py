"""Build task (lesson 12): a per-category gate, so a small category cannot hide inside the overall average."""
from collections import defaultdict


def category_gate(report, min_rate=0.8):
    """Return one reason per category whose pass rate is below min_rate (empty list = pass)."""
    totals, passed = defaultdict(int), defaultdict(int)
    for r in report["results"].values():
        totals[r["category"]] += 1
        passed[r["category"]] += r["pass"]
    return [f"{c}: {passed[c]}/{totals[c]} passed ({passed[c] / totals[c]:.0%}) < {min_rate:.0%}"
            for c in sorted(totals) if passed[c] / totals[c] < min_rate]
