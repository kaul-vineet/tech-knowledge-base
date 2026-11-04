import json
import unittest

import slo
from failure_lab import check
from traffic import END

NOW = END.timestamp()


def synthetic(n, errors=0, slow=0, route="GET /books", seconds=3600):
    """n requests spread over the last `seconds`; the first `errors` are 500s, the next `slow` take 2500 ms."""
    lines = []
    for i in range(n):
        t = NOW - seconds + i * seconds / n
        ts = slo.datetime.fromtimestamp(t, slo.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines.append(json.dumps({"ts": ts, "route": route, "status": 500 if i < errors else 200,
                                 "ms": 2500.0 if errors <= i < errors + slow else 40.0}))
    return slo.parse(lines)


class SliTest(unittest.TestCase):
    def test_burn_rate_is_bad_ratio_over_budget(self):
        records = synthetic(1000, errors=2)
        self.assertAlmostEqual(slo.burn_rate(records, "availability", NOW, 3600), 2.0)  # 0.2% / 0.1%

    def test_budget_consumed_is_burn_times_window_over_period(self):
        records = synthetic(3000, errors=3, seconds=3 * 86400)  # 0.1% bad over 3 days -> burn 1
        self.assertAlmostEqual(slo.budget_consumed(records, "availability", NOW), 0.10)

    def test_page_needs_both_windows(self):
        records = synthetic(1000, errors=20)  # 2% errors, all in the first minutes of the hour
        self.assertEqual(slo.burn_rate(records, "availability", NOW, 300), 0.0)
        fired = [(a["severity"], a["windows"]) for a in slo.alerts(records, NOW)]
        self.assertEqual(fired, [("ticket", "3d/6h")])  # 1h burns but 5m is clean again: no page; 6h still burns

    def test_ongoing_outage_pages(self):
        records = synthetic(1000, errors=1000)
        self.assertEqual([(a["severity"], a["windows"]) for a in slo.alerts(records, NOW)],
                         [("page", "1h/5m"), ("page", "6h/30m"), ("ticket", "3d/6h")])

    def test_percentile_nearest_rank(self):
        self.assertEqual([slo.percentile(list(range(1, 101)), p) for p in (50, 95, 99)], [50, 95, 99])

    def test_mean_check_flags_a_uniformly_slow_service(self):
        self.assertEqual(slo.latency_problems(synthetic(100, slow=100), NOW), ["mean latency 2500.0 ms > 200 ms"])


class FailureLabTest(unittest.TestCase):
    def test_symptom_mean_looks_fine_while_p99_is_broken(self):
        report, problems, fired = check(slo)
        self.assertEqual((report["mean"], report["p95"], report["p99"]), (147.9, 94.3, 2846.3))
        self.assertEqual((problems, fired), ([], []))

    def test_healthy_traffic_is_quiet(self):
        report, problems, fired = check(slo, incident=False)
        self.assertLess(report["p99"], 300)
        self.assertEqual((problems, fired), ([], []))


if __name__ == "__main__":
    unittest.main()
