import json
import pathlib
import shutil
import tempfile
import unittest

import fitness_policy
import handlers
import rbac
from app import CASES, HERE, call
from rego_lite import DecisionPoint, Policy, load_policy

BASE = load_policy(HERE / "policy" / "loans.rego")


class EngineTest(unittest.TestCase):
    def test_parses_rules_and_defaults(self):
        self.assertEqual([r[1] for r in BASE.rules], ["allow", "allow", "allow", "deny", "deny", "allowed"])
        self.assertEqual(BASE.defaults, {"allow": False, "allowed": False})

    def test_undefined_path_is_false_not_an_error(self):
        policy = Policy('package t\ndefault allow := false\nallow if {\n\tinput.missing.deep == 1\n}\n')
        self.assertEqual(policy.evaluate({})[0]["allow"], False)

    def test_not_in_and_count(self):
        policy = Policy('package t\nok if {\n\tnot "x" in input.tags\n\tcount(input.tags) == 2\n}\n')
        self.assertTrue(policy.evaluate({"tags": ["a", "b"]})[0]["ok"])
        self.assertFalse(policy.evaluate({"tags": ["x", "b"]})[0]["ok"] is True)


class DecisionLogTest(unittest.TestCase):
    def test_one_json_line_per_decision_with_email_erased(self):
        work = pathlib.Path(tempfile.mkdtemp(prefix=".tmp-", dir=HERE))
        self.addCleanup(shutil.rmtree, work, True)
        pdp = DecisionPoint(BASE, log_path=work / "d.jsonl")
        for c in CASES[:3]:
            call(pdp, c)
        events = [json.loads(line) for line in (work / "d.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["erased"], ["/input/subject/email"])
        self.assertNotIn("email", events[0]["input"]["subject"])
        self.assertEqual(events[0]["decision_id"], f"{BASE.revision}-000001")


    def test_log_lines_can_be_collected_in_memory(self):
        lines = []
        DecisionPoint(BASE, log_path=lines).decide(CASES[0]["input"])
        self.assertEqual(json.loads(lines[0])["result"], True)


class ComparisonTest(unittest.TestCase):
    def test_rbac_cannot_express_attribute_rules(self):
        self.assertEqual(sum(rbac.allowed(c["input"]) == c["allowed"] for c in CASES), 7)

    def test_symptom_base_policy_lets_librarians_cross_libraries(self):
        self.assertEqual(fitness_policy.gate_policy_tests(BASE)["value"], ["librarian of another library"])

    def test_handlers_raise_forbidden(self):
        pdp = DecisionPoint(load_policy(HERE / "solution" / "loans.rego"))
        member = {"id": "m1", "tenant": "lib00", "roles": ["member"]}
        with self.assertRaises(handlers.Forbidden):
            handlers.borrow(pdp, member, {"tenant": "lib00", "member_id": "m2", "active_loans": 0}, "b1")

    def test_pep_and_rule_coverage_gates(self):
        self.assertTrue(fitness_policy.gate_pep_coverage()["ok"])
        self.assertTrue(fitness_policy.gate_rule_coverage(BASE)["ok"])


if __name__ == "__main__":
    unittest.main()
