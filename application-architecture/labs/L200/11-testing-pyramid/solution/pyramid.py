"""Build task solution: pyramid.py plus speed budgets. Run: python pyramid.py --budget

A budget is a fitness function for test speed: a "unit" test that opens a file or a socket breaks it.
"""
import argparse
import math
import pathlib
import sys
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
# layer = file-name convention; the pyramid is many fast tests at the bottom, very few slow ones on top
LAYERS = [("unit", "test_unit*.py"), ("integration", "test_integration*.py"), ("e2e", "test_e2e*.py")]
BUDGET_MS = {"unit": 10, "integration": 1000, "e2e": 10000}  # mean per test; generous for shared CI runners


class TimedResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.durations = []

    def startTest(self, test):
        self._started = time.perf_counter()  # perf_counter: monotonic, highest available resolution
        super().startTest(test)

    def stopTest(self, test):
        self.durations.append(time.perf_counter() - self._started)
        super().stopTest(test)


def run_layer(pattern, start_dir=HERE):
    suite = unittest.TestLoader().discover(str(start_dir), pattern=pattern, top_level_dir=str(start_dir))
    result = TimedResult()
    started = time.perf_counter()
    suite.run(result)
    ran = result.testsRun - len(result.skipped)
    return {"tests": ran, "skipped": len(result.skipped), "failed": len(result.failures) + len(result.errors),
            "total_ms": (time.perf_counter() - started) * 1000,
            "mean_ms": sum(result.durations) * 1000 / max(ran, 1),
            "problems": [str(test) for test, _ in result.failures + result.errors]}


def shape_problems(rows):
    counts = [rows[name]["tests"] for name, _ in LAYERS]
    if not counts[0] >= counts[1] >= counts[2] >= 1:  # an "ice-cream cone" fails the check
        return [f"not a pyramid: unit {counts[0]}, integration {counts[1]}, e2e {counts[2]}"]
    return []


def budget_problems(rows, budgets=BUDGET_MS):
    return [f"{name}: mean {rows[name]['mean_ms']:.2f} ms is over the {limit} ms budget"
            for name, limit in budgets.items() if rows[name]["tests"] and rows[name]["mean_ms"] > limit]


def report(rows):
    print(f"{'layer':<12}{'tests':>6}{'skipped':>9}{'failed':>8}{'total ms':>10}{'mean ms':>9}")
    for name, _ in LAYERS:
        r = rows[name]
        print(f"{name:<12}{r['tests']:>6}{r['skipped']:>9}{r['failed']:>8}{r['total_ms']:>10.1f}{r['mean_ms']:>9.2f}")
    unit, e2e = rows["unit"]["mean_ms"], rows["e2e"]["mean_ms"]
    ratio = e2e / max(unit, 1e-6)
    print(f"one e2e test costs about as much as {ratio:,.0f} unit tests (about 10^{round(math.log10(ratio))})")


def main(argv=None, start_dir=HERE):
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", action="store_true", help="fail when a layer's mean test time is over budget")
    args = parser.parse_args(argv)
    rows = {name: run_layer(pattern, start_dir) for name, pattern in LAYERS}
    report(rows)
    problems = [p for r in rows.values() for p in r["problems"]] + shape_problems(rows)
    if args.budget:
        problems += budget_problems(rows)
    for problem in problems:
        print("PROBLEM", problem)
    print("pyramid OK" if not problems else "pyramid FAILED")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
