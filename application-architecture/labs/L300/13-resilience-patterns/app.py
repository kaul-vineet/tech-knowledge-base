"""Lesson 13 demo: the circuit breaker's states around a catalogue that goes down and comes back.

Run: python app.py   (JSON-lines log of every breaker transition and call outcome on stdout)
"""
import time

from deps import Catalogue, Members
from loans_service import build_service
from resilience import json_log


def main():
    catalogue = Catalogue(mode="up")
    log = []
    service = build_service(Members(), catalogue, log=lambda record: (log.append(record), json_log(record)))

    def borrow(n, label):
        calls_before = catalogue.calls
        results = [service.borrow("m1", f"b{i}") for i in range(n)]
        degraded = sum(r["degraded"] for r in results)
        print(f"# {label}: {n} borrows, {degraded} with fallback title, catalogue called {catalogue.calls - calls_before}x,"
              f" breaker {service.breaker.state}")

    borrow(3, "catalogue up")
    catalogue.mode = "down"
    borrow(8, "catalogue down")
    time.sleep(0.35)  # longer than open_s = 0.3: the next call is a half-open trial
    borrow(1, "still down, after open_s")
    catalogue.mode = "up"
    time.sleep(0.35)
    borrow(3, "catalogue back, after open_s")
    service.close()
    print("# transitions:", " -> ".join(["closed"] + [r["to"] for r in log if r["evt"] == "breaker"]))


if __name__ == "__main__":
    main()
