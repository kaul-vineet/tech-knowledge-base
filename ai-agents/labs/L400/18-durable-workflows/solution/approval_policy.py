"""Solution (lesson 18 build task): a deadline. No decision within timeout_h -> 'timed_out' (the workflow escalates);
a signal that arrives after the deadline is ignored, so a late click cannot move money."""


def state(signals, since, now, timeout_h):
    deadline = since + timeout_h
    for name, by, ts in signals:
        if name in ("approve", "reject") and ts <= deadline:
            return "approved" if name == "approve" else "rejected"
    return "timed_out" if now > deadline else "waiting"
