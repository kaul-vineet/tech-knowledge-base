# Lab 08 - data logging: sample temperature and light once per interval,
# store each row with the V2 `log` module (MY_DATA on a real board) and
# print the same row as serial CSV (the export path in the simulator).
from microbit import *
try:
    import log                  # V2 only; on a V1 board -> serial CSV only
except ImportError:
    log = None

INTERVAL_MS = 1000
LABELS = ("temp", "light")      # column labels: set ONCE, before the first row


def setup():
    if log:
        # timestamp column "Time (seconds)" is added in front of the labels
        log.set_labels(*LABELS, timestamp=log.SECONDS)
    print("time_ms," + ",".join(LABELS))   # serial CSV header (our own format)


def sample():
    return {"temp": temperature(), "light": display.read_light_level()}


def to_csv(t_ms, row):
    # one CSV record: same column order as the header, numbers only, no quotes needed
    return ",".join([str(t_ms)] + [str(row[k]) for k in LABELS])


def new_state():
    return {"rows": 0, "logging": log is not None}


def step(state):
    row = sample()
    if state["logging"]:
        log.add(row)            # dict form; raises OSError(28) when the log is full
    print(to_csv(running_time(), row))
    state["rows"] += 1
    display.show(Image.SQUARE_SMALL if state["rows"] % 2 else Image.SQUARE, wait=False)
    return row


def main():
    setup()
    state = new_state()
    while True:
        step(state)
        sleep(INTERVAL_MS)      # sampling interval (run_every is the scheduled alternative)


if __name__ == "__main__":
    main()
