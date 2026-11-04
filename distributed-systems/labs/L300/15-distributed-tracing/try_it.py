"""tryIt experiments for lesson 15 (python try_it.py). Prints what actually happens (times vary by a few ms)."""
import solution_tracing as sol
from analyze import critical_path, traces

# tryIt 1: the caller sends traceparent headers; which ones does the gateway continue?
for header in ("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",   # W3C example: valid
               "00-4BF92F3577B34DA6A3CE929D0E0E4736-00F067AA0BA902B7-01",   # uppercase hex: invalid
               "00-00000000000000000000000000000000-00f067aa0ba902b7-01"):  # all-zero trace id: invalid
    spans = sol.run_checkout(headers={"traceparent": header})
    gw = [s for s in spans if s["service"] == "gateway"][0]
    print(f"tryIt 1: {header[:20]}... -> gateway trace {gw['trace_id'][:12]}.., parent {gw['parent_id']}",
          f"| traces: {len(traces(spans))}")

# tryIt 2: payments /authorize gets 3x slower (60 -> 180 ms): how much of the checkout is it now?
for work in (0.06, 0.18):
    sol.WORK["/authorize"] = work
    spans = sol.run_checkout()
    root = min((s for s in spans if s["parent_id"] is None), key=lambda s: s["start"])
    auth = [s for s in spans if s["name"] == "GET /authorize"][0]
    on_path = auth in [s for s, _ in critical_path(spans, root)]
    share = (auth["end"] - auth["start"]) / (root["end"] - root["start"])
    print(f"tryIt 2: authorize work {work * 1000:.0f} ms -> its span is {share:.0%} of the checkout, on the critical path: {on_path}")
sol.WORK["/authorize"] = 0.06
