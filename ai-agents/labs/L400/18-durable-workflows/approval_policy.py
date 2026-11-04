"""Build task (lesson 18): what a waiting approval step decides on each run.

Shipped UNFIXED: it waits forever and accepts an approval that arrives after any deadline.
signals = [(name, by, ts_hours)] in arrival order; since / now in hours (fake clock).
Return 'approved' | 'rejected' | 'waiting' | 'timed_out'.
"""


def state(signals, since, now, timeout_h):
    for name, by, ts in signals:
        if name in ("approve", "reject"):
            return "approved" if name == "approve" else "rejected"
    return "waiting"
