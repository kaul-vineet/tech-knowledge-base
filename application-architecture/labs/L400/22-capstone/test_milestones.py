"""One test class per capstone milestone (M1-M5), on one seeded run without faults."""
import json
import pathlib
import unittest

import consumer
import loans_service
import run_capstone
import scorecard
from reuse import rego_lite, strangler

HERE = pathlib.Path(__file__).resolve().parent


class Run:
    evidence, rows = None, None

    @classmethod
    def get(cls):
        if cls.evidence is None:
            cls.evidence = scorecard.build()
            cls.rows = {r["criterion"]: r for r in run_capstone.criteria(cls.evidence)}
        return cls.evidence, cls.rows


class M1StrangleTest(unittest.TestCase):
    def test_cut_over_after_a_clean_parallel_run(self):
        e, rows = Run.get()
        self.assertEqual((e["cutover"]["mismatch_rate"], e["facade_mode"]), (0.0, "service"))
        self.assertTrue(rows["no new legacy callers"]["pass"])


class M2TenancyTest(unittest.TestCase):
    def test_guard_static_gate_and_probes(self):
        e, rows = Run.get()
        self.assertEqual(e["service"].guard_violations, [])
        self.assertEqual(scorecard.unscoped_sql(), [])
        self.assertEqual(e["probes"], {"cross_rows": 0, "cross_allowed": 0, "attempts": 10})


class M3PolicyTest(unittest.TestCase):
    def test_policy_cases_pep_and_private_decision_log(self):
        e, rows = Run.get()
        self.assertEqual(rows["policy requirement cases"]["value"], "14/14")
        self.assertEqual(scorecard.pep_gaps(), [])
        self.assertEqual(len(e["decision_log"]), 615)
        self.assertFalse(any('"email"' in line for line in e["decision_log"]))

    def test_member_cannot_read_another_members_loans(self):
        pdp = rego_lite.DecisionPoint(rego_lite.load_policy(scorecard.POLICY_FIXED))
        service = loans_service.LoansService(pdp, strangler.Facade(strangler.LegacyFines(), None))
        with self.assertRaises(loans_service.Forbidden):
            service.loans_of({"id": "m1", "tenant": "lib00", "roles": ["member"]}, "lib00", "m2")
        self.assertEqual(json.loads(service.request_log[-1])["status"], 403)


class M4EventsTest(unittest.TestCase):
    def test_outbox_relay_and_idempotent_consumers(self):
        e, _ = Run.get()
        self.assertEqual(e["events"], {"committed_changes": 469, "outbox_rows": 469, "unpublished": 0,
                                       "published": 469, "projection_mismatches": 0})


class M5CiTest(unittest.TestCase):
    def test_slo_contract_capacity_and_adrs(self):
        _, rows = Run.get()
        for name in ("availability SLI", "latency SLI", "burn-rate alerts", "consumer contract", "capacity N+1",
                     "ADR log"):
            self.assertTrue(rows[name]["pass"], rows[name])

    def test_consumer_side_writes_the_contract(self):
        self.assertEqual(consumer.build().name, "member-portal--loans-service.json")

    def test_scorecard_is_go(self):
        _, rows = Run.get()
        self.assertEqual([r for r in rows.values() if not r["pass"]], [])


if __name__ == "__main__":
    unittest.main()
