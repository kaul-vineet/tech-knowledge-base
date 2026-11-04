"""One test per milestone on the seeded run (seed 4). Run from the lab folder:
python -m unittest discover -s tests -t .      (Windows: py -m unittest discover -s tests -t .)"""
import unittest

from tests._shared import run
import api  # noqa: E402
import contracts  # noqa: E402
import laws  # noqa: E402
import run_project  # noqa: E402


class M1OfflineFirstDevices(unittest.TestCase):
    def test_every_minute_sampled_into_flash_none_dropped(self):
        r = run()
        self.assertEqual(r["sampled"], 20 * 12 * 60)
        self.assertEqual(r["dropped_flash_full"], 0)
        self.assertLessEqual(r["peak_log"], r["boards"][0].lab.MAX_LOG)

    def test_reboot_keeps_the_flash_log_and_bumps_boot(self):
        st = run()["states"]["d07"]
        self.assertEqual(st["flash"]["boot"], 2)
        self.assertEqual(st["seq"], 12 * 60 - 300)       # seq restarted at 1 after the reboot at minute 300


class M2DeltaSync(unittest.TestCase):
    def test_every_reading_reached_a_gateway_and_logs_drained(self):
        r = run()
        self.assertEqual(r["reached_gateway"], r["sampled"])
        self.assertTrue(r["logs_empty"])
        self.assertGreater(r["air"]["lost"], 0)          # the radio really was lossy


class M3CrdtGossip(unittest.TestCase):
    def test_merge_laws_hold(self):
        self.assertEqual(laws.check(seed=4, trials=200)["passed"], 200)

    def test_replicas_equal_and_values_exact(self):
        r = run()
        self.assertTrue(r["replicas_equal"])
        self.assertEqual(r["wrong_values"], 0)

    def test_law_check_catches_a_broken_merge(self):
        import store
        original = store.ReadingStore.merge

        def bad_merge(self, other):                      # mutation: keep MY readings only
            out = original(self, store.ReadingStore())
            return out
        store.ReadingStore.merge = bad_merge
        try:
            self.assertLess(laws.check(seed=4, trials=100)["passed"], 100)
        finally:
            store.ReadingStore.merge = original


class M4ApiContracts(unittest.TestCase):
    def test_contracts_verify_against_the_live_api(self):
        problems, tiles, deprecation, walked = run_project.api_and_contracts(run()["stores"]["b1"])
        self.assertEqual(problems, {"dashboard-v1--fleet-api.json": [], "dashboard-v2--fleet-api.json": []})
        self.assertEqual(deprecation, "@1798761600")
        self.assertEqual(walked, 14400)
        self.assertIn("d17 1.1 20 C light n/a (fw 1)", tiles)

    def test_latest_is_by_boot_and_seq_not_wall_time(self):
        body, _ = api.latest(run()["stores"]["b1"], "d07", 2)
        self.assertEqual((body["boot"], body["seq"]), (2, 420))

    def test_v1_reports_seq_that_restarted(self):
        body, headers = api.latest(run()["stores"]["b1"], "d07", 1)
        self.assertEqual(body["seq"], 420)               # v1 cannot say which boot: documented in the API
        self.assertIn("Sunset", headers)


if __name__ == "__main__":
    unittest.main()
