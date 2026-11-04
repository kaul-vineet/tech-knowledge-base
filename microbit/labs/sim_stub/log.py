"""Stub of the micro:bit V2 MicroPython `log` (data logging) module.

API per https://microbit-micropython.readthedocs.io/en/v2-docs/log.html
  set_labels(*labels, timestamp=SECONDS)  timestamp column first (None = off)
  add(data_dictionary=None, **kwargs)     new labels add a column + new header row;
                                          missing labels -> empty field;
                                          full log -> OSError(28) (ENOSPC)
  set_mirroring(serial)                   print each row to serial too
  delete(full=False)                      remove data AND headers
CSV details follow the CODAL runtime that the V2 firmware uses
(codal-microbit-v2 source/MicroBitLog.cpp): heading "Time (seconds)" etc.,
comma-separated rows, two decimals for every unit except milliseconds,
mirrored rows end with "\\r\\n", a row with no values is not written.
Whether the browser simulator formats rows exactly like this is NOT verified.
Stub-only: the numeric values of the time-unit constants, and the capacity
(set with _set_capacity; the real MY_DATA size is not modelled).
The rows end up in `rows` (header lines included), like the CSV inside MY_DATA.
"""
import sys

ENOSPC = 28
MILLISECONDS, SECONDS, MINUTES, HOURS, DAYS = 1, 10, 600, 36000, 864000
_UNITS = {MILLISECONDS: "milliseconds", SECONDS: "seconds", MINUTES: "minutes",
          HOURS: "hours", DAYS: "days"}

rows = []
_state = {}


def _reset():
    del rows[:]
    _state.clear()
    _state.update(labels=[], timestamp=SECONDS, mirror=False, used=0,
                  capacity=None, full=False, header_dirty=False, has_data=False)


_reset()


def _now_ms():
    import microbit
    return microbit.running_time()


def _stamp(ms, unit):
    if unit == MILLISECONDS:
        return str(ms)
    t = ms // unit                       # hundredths of the unit
    return "%d.%02d" % (t // 100, t % 100)


def _heading(unit):
    return "Time (%s)" % _UNITS[unit]


def _write(line):
    size = len(line) + 1
    if _state["capacity"] is not None and _state["used"] + size > _state["capacity"]:
        _state["full"] = True
        raise OSError(ENOSPC)
    _state["used"] += size
    rows.append(line)
    if _state["mirror"]:
        sys.stdout.write(line + "\r\n")


def _add_label(label):
    if label not in _state["labels"]:
        _state["labels"].append(label)
        _state["header_dirty"] = True


def set_labels(*labels, timestamp=SECONDS):
    if timestamp is not None and timestamp not in _UNITS:
        raise ValueError("invalid timestamp unit")
    if not _state["has_data"]:
        # before the first row the timestamp column can still be replaced
        _state["labels"] = [l for l in _state["labels"] if not l.startswith("Time (")]
        if timestamp is not None:
            _state["labels"].insert(0, _heading(timestamp))
        _state["header_dirty"] = True
    _state["timestamp"] = timestamp
    for label in labels:
        _add_label(str(label))


def set_mirroring(serial):
    _state["mirror"] = bool(serial)


def delete(full=False):
    mirror, capacity = _state["mirror"], _state["capacity"]
    _reset()
    _state["mirror"], _state["capacity"] = mirror, capacity


def add(data_dictionary=None, **kwargs):
    if _state["full"]:
        raise OSError(ENOSPC)
    data = dict(data_dictionary or {})
    data.update(kwargs)
    if not data:
        return
    unit = _state["timestamp"]
    if not _state["labels"] and unit is not None:
        _state["labels"].append(_heading(unit))
    for key in data:
        _add_label(str(key))
    values = {str(k): str(v) for k, v in data.items()}
    if unit is not None:
        values[_heading(unit)] = _stamp(_now_ms(), unit)
    if _state["header_dirty"]:
        _write(",".join(_state["labels"]))
        _state["header_dirty"] = False
    _write(",".join(values.get(l, "") for l in _state["labels"]))
    _state["has_data"] = True


# ---- test helpers
def _set_capacity(n_bytes):
    """Make the log 'full' after n_bytes of CSV (header + rows)."""
    _state["capacity"] = n_bytes


def _csv():
    return "\n".join(rows) + ("\n" if rows else "")
