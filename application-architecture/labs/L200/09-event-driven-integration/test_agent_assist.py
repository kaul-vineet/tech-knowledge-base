import contextlib
import io
import json
import pathlib
import sys
import unittest

import agent_assist
from agent_assist import BRIEF, SAMPLE, propose, validate_proposal
from asyncapi_check import load

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent / "_shared"))
from local_agent import fake_model_server  # noqa: E402


def good_fragment():
    props = {"eventId": {"type": "string", "format": "uuid"}, "eventType": {"type": "string", "const": "LoanOverdue"},
             "occurredAt": {"type": "string", "format": "date-time"}, "loanId": {"type": "integer"},
             "bookId": {"type": "string"}, "memberId": {"type": "string"}, "daysOverdue": {"type": "integer"}}
    return {"channels": {"loanOverdue": {"address": "library.loans.overdue",
                                         "messages": {"LoanOverdue": {"$ref": "#/components/messages/LoanOverdue"}}}},
            "operations": {"sendLoanOverdue": {"action": "send", "channel": {"$ref": "#/channels/loanOverdue"},
                                               "messages": [{"$ref": "#/channels/loanOverdue/messages/LoanOverdue"}]}},
            "components": {"messages": {"LoanOverdue": {"payload": {"$ref": "#/components/schemas/LoanOverduePayload"}}},
                           "schemas": {"LoanOverduePayload": {"type": "object", "required": sorted(SAMPLE),
                                                              "properties": props}}}}


class ValidateProposalTest(unittest.TestCase):
    def test_good_fragment_passes(self):
        merged, problems = validate_proposal(json.dumps(good_fragment()))
        self.assertEqual(problems, [])
        self.assertIn("loanOverdue", merged["channels"])

    def test_prose_is_rejected(self):
        self.assertEqual(validate_proposal("Sure! Here is the schema.")[1], ["reply is not a single parseable object"])

    def test_cannot_replace_existing_contract(self):
        fragment = good_fragment()
        fragment["channels"]["loanCreated"] = {"address": "hijacked", "messages": {}}
        self.assertIn("channels.loanCreated already exists - proposals may only add",
                      validate_proposal(json.dumps(fragment))[1])

    def test_sample_event_from_code_is_the_judge(self):
        fragment = good_fragment()
        fragment["components"]["schemas"]["LoanOverduePayload"]["properties"]["daysOverdue"] = {"type": "string"}
        self.assertEqual(validate_proposal(json.dumps(fragment))[1],
                         ["sample event from code: payload.daysOverdue: expected string, got int 3"])

    def test_base_document_is_not_modified(self):
        validate_proposal(json.dumps(good_fragment()))
        self.assertNotIn("loanOverdue", load()["channels"])


class FakeModelLoopTest(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_model_server.start_in_thread()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def test_first_reply_rejected_then_fixed(self):
        merged, problems, log = propose(self.url, "fake-model")
        self.assertEqual(problems, [])
        self.assertTrue(log[0].startswith("attempt 1: REJECTED"))
        self.assertIn("action must be 'send' or 'receive' (AsyncAPI 3), got 'publish'", log[0])
        self.assertEqual(log[1], "attempt 2: OK")
        self.assertEqual(merged["operations"]["sendLoanOverdue"]["action"], "send")

    def test_main_prints_unchanged_file(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(agent_assist.main([]), 0)
        self.assertIn("asyncapi.json unchanged: True", out.getvalue())
        self.assertEqual(BRIEF["Channel"], "loanOverdue")


if __name__ == "__main__":
    unittest.main()
