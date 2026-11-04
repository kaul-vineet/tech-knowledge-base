import pathlib
import tempfile
import unittest

import fines_service
import fitness_legacy
from strangler import Facade, LegacyFines, ParallelRun, ServiceFines, bucket, cutover_decision, replay
from traffic import requests

HERE = pathlib.Path(__file__).resolve().parent


class Boom:
    def fine(self, *args):
        raise TimeoutError("service down")


class ParallelRunTest(unittest.TestCase):
    def test_returns_control_and_counts_mismatch(self):
        run = ParallelRun(LegacyFines(), ServiceFines(fn=fines_service.fine_for))
        self.assertEqual(run.fine(3, "student"), "0.13")  # legacy answer, although the service says 0.12
        self.assertEqual(run.stats, {"comparisons": 1, "mismatches": 1, "candidate_errors": 0})

    def test_candidate_error_never_reaches_the_member(self):
        run = ParallelRun(LegacyFines(), Boom())
        self.assertEqual(run.fine(10, "adult"), "2.00")
        self.assertEqual(run.stats["candidate_errors"], 1)

    def test_mismatches_are_logged_as_json_lines(self):
        with tempfile.TemporaryDirectory(prefix=".tmp-", dir=HERE) as tmp:
            log = pathlib.Path(tmp) / "m.jsonl"
            run = ParallelRun(LegacyFines(), ServiceFines(fn=fines_service.fine_for), log)
            run.fine(7, "student")
            self.assertIn('"candidate": "0.62"', log.read_text(encoding="utf-8"))


class FacadeTest(unittest.TestCase):
    def test_symptom_base_service_mismatch_rate(self):
        facade = Facade(LegacyFines(), ServiceFines(fn=fines_service.fine_for), mode="shadow")
        replay(facade, list(requests()))
        self.assertEqual(facade.shadow.stats, {"comparisons": 2000, "mismatches": 108, "candidate_errors": 0})
        self.assertFalse(cutover_decision(facade.shadow.stats)["ready"])

    def test_canary_is_sticky_per_member(self):
        self.assertEqual(bucket("m42"), bucket("m42"))
        facade = Facade(LegacyFines(), Boom(), mode="canary", canary_pct=0)
        self.assertEqual(facade.fine("m1", 5, "adult"), "0.75")  # 0 % canary: legacy only

    def test_over_http(self):
        server, url = fines_service.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.assertEqual(ServiceFines(base_url=url).fine(40, "adult"), "9.50")


class CutoverTest(unittest.TestCase):
    def test_criteria(self):
        self.assertTrue(cutover_decision({"comparisons": 1000, "mismatches": 1, "candidate_errors": 0})["ready"])
        self.assertIn("only 999 comparisons (< 1000)",
                      cutover_decision({"comparisons": 999, "mismatches": 0, "candidate_errors": 0})["reasons"])
        self.assertFalse(cutover_decision({"comparisons": 5000, "mismatches": 0, "candidate_errors": 1})["ready"])


class FitnessTest(unittest.TestCase):
    def test_no_new_legacy_callers(self):
        result = fitness_legacy.gate()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["value"]["callers"], 2)

    def test_planted_caller_fails(self):
        with tempfile.TemporaryDirectory(prefix=".tmp-", dir=HERE) as tmp:
            folder = pathlib.Path(tmp)
            (folder / "legacy_callers.json").write_text('{"allowed": ["strangler.py"]}', encoding="utf-8")
            (folder / "strangler.py").write_text("import legacy_monolith\n", encoding="utf-8")
            (folder / "new_report.py").write_text("from legacy_monolith import calculate_fine\n", encoding="utf-8")
            result = fitness_legacy.gate(folder, folder / "legacy_callers.json")
            self.assertEqual((result["ok"], result["value"]["new"]), (False, ["new_report.py"]))


if __name__ == "__main__":
    unittest.main()
