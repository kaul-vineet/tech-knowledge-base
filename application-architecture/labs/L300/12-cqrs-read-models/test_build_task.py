"""Build task check (lesson 12): a crash never loses an event, and a replayed event changes nothing.

By default this checks solution/projector.py. To check your edited projector.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

from failure_lab import crash_and_restart, seeded_history

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("projector.py" if os.environ.get("CHECK_MINE") else "solution/projector.py")
spec = importlib.util.spec_from_file_location("projector_under_test", TARGET)
pj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pj)


class HardenedProjectorTest(unittest.TestCase):
    def test_crash_then_restart_leaves_no_drift(self):
        store, projector, crashed, last = crash_and_restart(pj)
        self.assertEqual(crashed, "projector died at seq 31")
        self.assertEqual(projector.position(), last)
        self.assertEqual(pj.drift(store, projector.db, pj.Projector), [])

    def test_checkpoint_does_not_move_past_a_crash(self):
        store = seeded_history()
        projector = pj.Projector(store, log=lambda record: None, crash_at_seq=5)
        with self.assertRaises(pj.SimulatedCrash):
            projector.run_once()
        self.assertEqual(projector.position(), 4)  # event 5 was not applied, so it is still to do

    def test_replayed_event_changes_nothing(self):
        store = seeded_history()
        projector = pj.Projector(store, log=lambda record: None)
        projector.run_once()
        before = pj.LoansView(projector.db).snapshot()
        with projector.db:  # at-least-once: the last 3 events arrive again
            projector.db.execute("UPDATE checkpoint SET seq = seq - 3")
        self.assertEqual(projector.run_once(), 3)
        self.assertEqual(pj.LoansView(projector.db).snapshot(), before)


if __name__ == "__main__":
    unittest.main()
