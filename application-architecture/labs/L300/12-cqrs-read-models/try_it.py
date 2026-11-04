"""Try it (lesson 12): a slower projector, and a 'half fix' that only reorders the checkpoint. Run: python try_it.py"""
import projector as base
from app import percentile, run
from failure_lab import seeded_history


def try_1_slower_poll():
    for poll_s in (0.02, 0.2):
        records = run(poll_s=poll_s)[3]
        lags = [r["lag_ms"] for r in records if r["evt"] == "projected"]
        print(f"[1] poll every {int(poll_s * 1000):>3} ms -> consistency window p50 {percentile(lags, 50)} ms, "
              f"max {max(lags)} ms")


class CheckpointAfterApply(base.Projector):
    """Half fix: apply first, checkpoint second - still two transactions, still `active + 1`."""

    def run_once(self):
        events = self.store.read_after(self.position())
        for seq, event_type, data, _ in events:
            with self.db:
                self.apply(event_type, data)
            if seq == self.crash_at_seq:
                raise base.SimulatedCrash(f"projector died at seq {seq}, after apply, before checkpoint")
            self._save_checkpoint(seq)
        return len(events)


def try_2_half_fix():
    store = seeded_history()
    first = CheckpointAfterApply(store, log=lambda record: None, crash_at_seq=31)
    try:
        first.run_once()
    except base.SimulatedCrash as exc:
        print(f"[2] {exc}")
    CheckpointAfterApply(store, read_db=first.db, log=lambda record: None).run_once()
    print(f"[2] restart -> drift: {base.drift(store, first.db)}")


if __name__ == "__main__":
    try_1_slower_poll()
    try_2_half_fix()
