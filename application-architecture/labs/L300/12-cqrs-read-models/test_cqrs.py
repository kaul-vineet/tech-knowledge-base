import io
import json
import unittest

from app import run
from failure_lab import crash_and_restart
from projector import LoansView, Projector, drift, json_log
import projector as base
from write_model import EventStore, LoanCommands, LoanRuleViolation


class WriteSideTest(unittest.TestCase):
    def test_aggregate_rejects_fourth_loan_and_records_nothing(self):
        store = EventStore()
        commands = LoanCommands(store)
        for book in ("b1", "b2", "b3"):
            commands.borrow("m1", book)
        with self.assertRaises(LoanRuleViolation):
            commands.borrow("m1", "b4")
        self.assertEqual(len(store.read_after(0)), 3)


class ReadSideTest(unittest.TestCase):
    def setUp(self):
        self.store = EventStore()
        self.commands = LoanCommands(self.store)
        self.projector = Projector(self.store, log=lambda record: None)
        self.view = LoansView(self.projector.db)

    def test_view_is_behind_until_the_projector_runs(self):
        self.commands.borrow("m1", "b1")
        self.assertIsNone(self.view.holder("b1"))  # eventual consistency: not visible yet
        self.projector.run_once()
        self.assertEqual((self.view.holder("b1"), self.view.active_loans("m1")), ("m1", 1))

    def test_return_updates_both_tables(self):
        self.commands.borrow("m1", "b1")
        self.commands.give_back("m1", "b1")
        self.projector.run_once()
        self.assertEqual((self.view.holder("b1"), self.view.active_loans("m1")), (None, 0))
        self.assertEqual(self.projector.position(), 2)

    def test_rebuild_reproduces_the_view(self):
        for member, book in [("m1", "b1"), ("m2", "b2"), ("m1", "b3")]:
            self.commands.borrow(member, book)
        self.projector.run_once()
        before = self.view.snapshot()
        self.assertEqual(self.projector.rebuild(), 3)
        self.assertEqual(self.view.snapshot(), before)

    def test_drift_finds_a_tampered_row(self):
        self.commands.borrow("m1", "b1")
        self.projector.run_once()
        with self.projector.db:
            self.projector.db.execute("UPDATE member_loans SET active = 5")
        self.assertEqual(drift(self.store, self.projector.db), ["member_loans[m1]: view 5, events say 1"])

    def test_log_is_one_json_object_per_line(self):
        out = io.StringIO()
        self.commands.borrow("m1", "b1")
        Projector(self.store, log=lambda record: json_log(record, out)).run_once()
        record = json.loads(out.getvalue().splitlines()[0])
        self.assertEqual((record["evt"], record["seq"], record["type"]), ("projected", 1, "LoanCreated"))
        self.assertGreaterEqual(record["lag_ms"], 0)


class FailureLabTest(unittest.TestCase):
    def test_symptom_base_projector_misses_an_event_after_a_crash(self):
        store, projector, crashed, last = crash_and_restart(base)
        self.assertEqual((crashed, projector.position(), last), ("projector died at seq 31", 33, 33))
        self.assertEqual(drift(store, projector.db),
                         ["member_loans[m3]: view 1, events say 2", "book_status[b6]: view None, events say 'm3'"])
        projector.rebuild()  # recovery for a view that is already wrong
        self.assertEqual(drift(store, projector.db), [])


class DemoTest(unittest.TestCase):
    def test_threaded_run_converges(self):
        store, projector, view, records, events, rejected, stale = run(n=20, poll_s=0.01)
        self.assertEqual(projector.position(), events)
        self.assertEqual(len([r for r in records if r["evt"] == "projected"]), events)
        self.assertEqual(drift(store, projector.db), [])


if __name__ == "__main__":
    unittest.main()
