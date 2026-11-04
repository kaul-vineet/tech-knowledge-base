"""Agent assist tests: run against the deterministic fake model server only (no network, no real model)."""
import contextlib
import io
import unittest

import agent_assist
from agent_assist import BRIEF, DOCS, build_prompt, draft_adr, next_adr_number, validate_draft
from local_agent import fake_model_server

GOOD = ("# ADR 2: Modules talk only through public interfaces\n\n## Context\n\nc\n\n## Decision\n\n"
        "We will ... check_boundaries.py fails the build.\n\n## Status\n\nProposed.\n\n## Consequences\n\nx\n")


class ValidateDraftTest(unittest.TestCase):
    def test_good_draft_passes(self):
        self.assertEqual(validate_draft(GOOD, 2), [])

    def test_accepted_status_is_rejected(self):
        problems = validate_draft(GOOD.replace("Proposed.", "Accepted."), 2)
        self.assertTrue(any("Proposed" in p for p in problems))

    def test_wrong_number_is_rejected(self):
        self.assertTrue(any("number 2" in p for p in validate_draft(GOOD.replace("ADR 2", "ADR 1"), 2)))

    def test_missing_section_is_rejected(self):
        self.assertTrue(validate_draft(GOOD.split("## Consequences")[0], 2))

    def test_decision_must_name_the_check(self):
        problems = validate_draft(GOOD.replace("check_boundaries.py", "a script"), 2)
        self.assertIn("Decision must name its automated check check_boundaries.py", problems)


class FakeModelLoopTest(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_model_server.start_in_thread()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_first_draft_rejected_then_fixed_by_feedback(self):
        draft, problems, log = draft_adr(self.url, "fake-model", 2)
        self.assertTrue(log[0].startswith("attempt 1: REJECTED"))
        self.assertIn("got 'Accepted'", log[0])
        self.assertEqual(log[1], "attempt 2: OK")
        self.assertEqual(problems, [])
        self.assertTrue(draft.startswith(f"# ADR 2: {BRIEF['Title']}"))

    def test_one_attempt_only_leaves_the_draft_rejected(self):
        _, problems, _ = draft_adr(self.url, "fake-model", 2, attempts=1)
        self.assertTrue(problems)


class BoundaryStaysAuthoritativeTest(unittest.TestCase):
    def test_prompt_has_no_words_that_trigger_other_fake_rules(self):
        prompt = build_prompt(2).lower()
        self.assertNotIn("json", prompt)
        self.assertNotIn("sentiment", prompt)

    def test_boundary_result_comes_from_the_checker(self):
        code, summary = agent_assist.boundary_check()
        self.assertEqual((code, summary), (0, "checked 7 files: 0 boundary violation(s)"))

    def test_main_never_writes_into_doc_arch(self):
        before = sorted(p.name for p in DOCS.iterdir())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(agent_assist.main([]), 0)
        self.assertEqual(sorted(p.name for p in DOCS.iterdir()), before)
        self.assertEqual(next_adr_number(), 2)
        self.assertIn("fitness function (authoritative)", out.getvalue())


if __name__ == "__main__":
    unittest.main()
