"""Build task (lesson 12) - YOUR FILE. Shipped UNFIXED: it gates on the overall pass rate only, so the
2-ticket 'account' category can collapse to 0% while the average still says 90%.

TODO: group the results by r["category"] and return one reason per category below min_rate, e.g.
"account: 0/2 passed (0%) < 80%". Check it: BUILD_TARGET=mine python -m unittest -v test_build_task
"""


def category_gate(report, min_rate=0.8):
    """Return one reason per failing check (empty list = pass)."""
    results = list(report["results"].values())
    rate = sum(r["pass"] for r in results) / len(results)  # one average: a small category hides inside it
    return [] if rate >= min_rate else [f"overall: {rate:.0%} < {min_rate:.0%}"]
