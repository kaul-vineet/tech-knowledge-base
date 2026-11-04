"""M5: fitness functions reused from lessons 17, 19 and 21, plus secret handling (lesson 16)."""
import unittest
from pathlib import Path

import paths  # noqa: F401  (puts the reused lab folders on sys.path)
import agility_lint
import solution_verified
import test_fitness_no_key_export as l19
from capstone_testing import ServiceCase
from secrets_app import scan_log

HERE = Path(__file__).resolve().parent


class TestM5(ServiceCase):
    docs = 1

    def test_no_hard_coded_algorithms(self):
        self.assertEqual(agility_lint.scan([HERE]), [])

    def test_no_key_export(self):
        self.assertEqual(l19.key_export_calls([HERE]), [])
        self.assertEqual(l19.inventory(self.ns.token), [])

    def test_threat_model_clean(self):
        self.assertEqual(solution_verified.check(solution_verified.load(HERE / "threat_model.json")), [])

    def test_no_secrets_in_logs(self):
        self.ns.log.debug("upstream call", extra={"ctx": {"authorization": "Bearer " + "z" * 24, "pin": self.ns.pin.reveal()}})
        self.assertEqual(scan_log(self.ns.log_stream.getvalue(), known=[self.ns.pin.reveal()]), [])


if __name__ == "__main__":
    unittest.main()
