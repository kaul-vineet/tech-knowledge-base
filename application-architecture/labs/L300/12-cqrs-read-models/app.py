"""Lesson 12 demo: commands on the write side, a projector thread builds the read model; measure the lag.

Run: python app.py   (writes the projector's JSON-lines log to out/projector.jsonl)
"""
import json
import pathlib
import random
import threading
import time

from projector import LoansView, Projector, drift
from write_model import EventStore, LoanCommands, LoanRuleViolation

HERE = pathlib.Path(__file__).resolve().parent
LOG = HERE / "out" / "projector.jsonl"


def workload(seed=12, n=40):
    rng, holder = random.Random(seed), {}  # seeded: the same commands every run
    for _ in range(n):
        free = [f"b{i}" for i in range(1, 9) if f"b{i}" not in holder]
        if free and (rng.random() < 0.65 or not holder):
            book, member = rng.choice(free), f"m{rng.randint(1, 3)}"
            holder[book] = member  # the client's guess; the aggregate may still reject it (max 3 loans)
            yield "borrow", member, book
        else:
            book = rng.choice(sorted(holder))
            yield "give_back", holder.pop(book), book


def percentile(values, p):  # nearest-rank percentile
    ordered = sorted(values)
    return ordered[max(0, -(-len(ordered) * p // 100) - 1)]


def run(seed=12, n=40, poll_s=0.02):
    store, records, lock = EventStore(), [], threading.Lock()
    commands, projector = LoanCommands(store), Projector(store, log=records.append)
    view, stop = LoansView(projector.db), threading.Event()

    def poll():  # the read side catches up on its own schedule: this is where eventual consistency comes from
        while not stop.is_set():
            with lock:
                projector.run_once()
            stop.wait(poll_s)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()
    events, rejected, stale = 0, 0, 0
    rng = random.Random(seed + 1)
    for action, member, book in workload(seed, n):
        try:
            getattr(commands, action)(member, book)
        except LoanRuleViolation:
            rejected += 1
            continue
        events += 1
        with lock:  # read-your-own-write straight after the command
            stale += view.holder(book) != (member if action == "borrow" else None)
        time.sleep(rng.uniform(0, 0.01))
    while projector.position() < events:
        time.sleep(0.005)
    stop.set()
    thread.join()
    return store, projector, view, records, events, rejected, stale


def main():
    store, projector, view, records, events, rejected, stale = run()
    lags = [r["lag_ms"] for r in records if r["evt"] == "projected"]
    print(f"write side : {events + rejected} commands -> {events} events, {rejected} rejected by the aggregate")
    print(f"read side  : consistency window from the projector log: p50 {percentile(lags, 50)} ms, "
          f"p95 {percentile(lags, 95)} ms, max {max(lags)} ms (poll every 20 ms)")
    print(f"stale reads: {stale} of {events} reads straight after the command did not see it yet")
    print(f"view       : {view.snapshot()['member_loans']}")
    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    print(f"log        : out/projector.jsonl ({len(records)} lines); first: {json.dumps(records[0], sort_keys=True)}")
    before = view.snapshot()
    replayed = projector.rebuild()
    print(f"rebuild    : replayed {replayed} events, view identical: {view.snapshot() == before}, "
          f"drift: {drift(store, projector.db)}")


if __name__ == "__main__":
    main()
