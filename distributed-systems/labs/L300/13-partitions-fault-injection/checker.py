"""A small linearizability checker for ONE read/write register (the idea behind Knossos and Porcupine).
A history is linearizable if every operation can be given one instant between its start and end so that,
in that order, the operations obey a single-copy register. Exhaustive search: fine for ~10 operations.
Failed operations had no effect and are left out (an indeterminate op would need both cases; not modelled)."""


def check_register(history, initial=0):
    """history: [{"process", "f": "read"|"write", "value", "start", "end", "ok"}]. Returns (ok, order)."""
    ops = [op for op in history if op["ok"]]

    def search(remaining, state, order):
        if not remaining:
            return order
        horizon = min(op["end"] for op in remaining)  # whatever goes next must have started by then
        for op in remaining:
            if op["start"] > horizon:
                continue  # another op finished before this one began: real-time order forbids it going first
            if op["f"] == "read" and op["value"] != state:
                continue  # a read must return the latest write in the chosen order
            found = search([o for o in remaining if o is not op], op["value"], order + [op])
            if found is not None:
                return found
        return None

    order = search(ops, initial, [])
    return order is not None, order


def describe(op):
    what = f"write {op['value']}" if op["f"] == "write" else f"read -> {op['value']}"
    return f"{op['process']} {what} via {op['node']} [{op['start']:g}, {op['end']:g}]"


def stale_reads(history):
    """Explains a failure: an ok read whose value no write could justify. W = the last write that finished before
    the read began; only W or a write that may be ordered after W (it ended after W began) can explain the read."""
    ok = [op for op in history if op["ok"]]
    found = []
    for read in (op for op in ok if op["f"] == "read"):
        done = [w for w in ok if w["f"] == "write" and w["end"] < read["start"]]
        if not done:
            continue
        last = max(done, key=lambda w: w["end"])
        allowed = {w["value"] for w in ok if w["f"] == "write" and w["end"] > last["start"] and w["start"] < read["end"]}
        if read["value"] not in allowed:
            found.append((read, last))
    return found
