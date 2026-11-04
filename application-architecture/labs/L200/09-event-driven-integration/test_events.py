import copy
import unittest
from unittest import mock

import outbox
from app import wire
from asyncapi_check import check_document, load, validate_event
from events import new_event
from outbox import BookAlreadyOnLoan, LoansWithOutbox, Relay


class OutboxTest(unittest.TestCase):
    def setUp(self):
        self.loans = LoansWithOutbox()
        self.relay, self.bus, self.notify, self.projection, self.problems = wire(self.loans)

    def count(self, table):
        return self.loans.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_change_and_event_commit_together(self):
        self.loans.borrow("b1", "m1")
        self.assertEqual((self.count("loans"), self.count("outbox")), (1, 1))

    def test_failed_event_rolls_back_the_change(self):
        with mock.patch.object(outbox, "new_event", side_effect=RuntimeError("event store down")):
            self.assertRaises(RuntimeError, self.loans.borrow, "b1", "m1")
        self.assertEqual((self.count("loans"), self.count("outbox")), (0, 0))

    def test_rule_violation_writes_no_event(self):
        self.loans.borrow("b1", "m1")
        self.assertRaises(BookAlreadyOnLoan, self.loans.borrow, "b1", "m2")
        self.assertEqual(self.loans.pending(), 1)

    def test_relay_publishes_in_commit_order_once(self):
        self.loans.borrow("b1", "m1")
        self.loans.give_back(1)
        self.loans.borrow("b2", "m1")
        self.assertEqual(self.relay.publish_pending(), 3)
        self.assertEqual([t for _, t in self.bus.delivered], ["LoanCreated", "LoanReturned", "LoanCreated"])
        self.assertEqual(self.relay.publish_pending(), 0)
        self.assertEqual(dict(self.projection.active), {"m1": 1})
        self.assertEqual(self.problems, [])

    def test_consumer_failure_keeps_event_pending(self):
        self.loans.borrow("b1", "m1")
        self.bus.subscribe("loanCreated", mock.Mock(side_effect=RuntimeError("mail server down")))
        self.assertRaises(RuntimeError, self.relay.publish_pending)
        self.assertEqual(self.loans.pending(), 1)

    def test_redelivery_is_ignored_by_idempotent_consumers(self):
        self.loans.borrow("b1", "m1")
        with mock.patch.object(Relay, "_mark_published", side_effect=RuntimeError("crash")):
            self.assertRaises(RuntimeError, self.relay.publish_pending)
        self.relay.publish_pending()  # same event again
        self.assertEqual((len(self.notify.sent), self.notify.duplicates), (1, 1))


class AsyncApiTest(unittest.TestCase):
    def setUp(self):
        self.doc = load()

    def test_document_is_structurally_valid(self):
        self.assertEqual(check_document(self.doc), [])
        self.assertEqual(self.doc["asyncapi"], "3.1.0")

    def test_detects_asyncapi_2_style_operation(self):
        doc = copy.deepcopy(self.doc)
        doc["operations"]["sendLoanCreated"]["action"] = "publish"
        self.assertIn("action must be 'send' or 'receive'", check_document(doc)[0])

    def test_detects_operation_pointing_at_unknown_channel(self):
        doc = copy.deepcopy(self.doc)
        doc["operations"]["sendLoanCreated"]["channel"] = {"$ref": "#/channels/loanLost"}
        self.assertIn("must be a $ref to a root channel", check_document(doc)[0])

    def test_event_validation(self):
        good = new_event("LoanCreated", {"loanId": 1, "bookId": "b1", "memberId": "m1"})
        self.assertEqual(validate_event(self.doc, "loanCreated", good), [])
        bad = {**good, "loanId": "1", "extra": True}
        del bad["memberId"]
        self.assertEqual(validate_event(self.doc, "loanCreated", bad), [
            "payload: missing required field 'memberId'", "payload: unexpected field 'extra'",
            "payload.loanId: expected integer, got str '1'"])
        wrong_type = new_event("LoanReturned", {"loanId": 1, "bookId": "b1", "memberId": "m1"})
        self.assertEqual(validate_event(self.doc, "loanCreated", wrong_type),
                         ["payload.eventType: must be 'LoanCreated', got 'LoanReturned'"])


if __name__ == "__main__":
    unittest.main()
