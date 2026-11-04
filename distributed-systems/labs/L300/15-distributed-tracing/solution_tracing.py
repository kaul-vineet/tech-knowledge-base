"""L300 lesson 15 BUILD-TASK REFERENCE (python solution_tracing.py): tracing.py + client middleware.
Original header: W3C Trace Context across three stdlib HTTP services on 127.0.0.1.
gateway /checkout -> orders /create -> payments /authorize, then gateway -> payments /receipt. Every service
records a span (JSON lines); analyze.py groups them into traces and finds the critical path.
Happy path: one trace, four spans. Fault: one hop forgets the traceparent header -> the trace breaks in two."""
import json, random, re, threading, time

from analyze import critical_path, problems, traces
from helpers import QuietHandler, serve
from helpers import call as raw_call

TRACEPARENT = re.compile(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})(-.*)?$")  # version-trace-parent-flags
WORK = {"/checkout": 0.005, "/create": 0.02, "/authorize": 0.06, "/receipt": 0.01}  # seconds of fake work
URL, SPANS, LOCK, CURRENT = {}, [], threading.Lock(), threading.local()
RNG = random.Random(15)  # seeded ids so runs are comparable; production ids come from a CSPRNG


def new_id(bits):
    with LOCK:
        return f"{RNG.getrandbits(bits):0{bits // 4}x}"


def parse_traceparent(value):
    """'00-<32 hex trace-id>-<16 hex parent-id>-<2 hex flags>' -> (trace_id, parent_id, flags), else None.
    All-zero ids, version ff and extra fields on version 00 are invalid; a higher version keeps its first four
    fields (W3C 3.2.4). An invalid or missing header means: start a NEW trace (W3C section 4)."""
    m = TRACEPARENT.match((value or "").strip())
    if not m or m[1] == "ff" or (m[1] == "00" and m[5]) or m[2] == "0" * 32 or m[3] == "0" * 16:
        return None
    return m[2], m[3], m[4]


def call(url, payload=None, headers=None, timeout=2.0):
    """Client MIDDLEWARE: every outgoing request - including old raw call() sites - carries the current trace
    context: my span id becomes the callee's parent-id; trace-id and flags pass through unchanged."""
    ctx = getattr(CURRENT, "span", None)
    if ctx:
        headers = {"traceparent": f"00-{ctx['trace_id']}-{ctx['span_id']}-{CURRENT.flags}", **(headers or {})}
    return raw_call(url, payload, headers, timeout)


traced_call = call  # one code path for propagation: no hop can forget it


class Service(QuietHandler):
    name, routes = "service", {}

    def do_GET(self):
        incoming = parse_traceparent(self.headers.get("traceparent"))  # header names are case-insensitive
        trace_id, parent_id, flags = incoming or (new_id(128), None, "01")  # new trace: sampled
        span = {"trace_id": trace_id, "span_id": new_id(64), "parent_id": parent_id, "service": self.name,
                "name": f"GET {self.path}", "start": time.perf_counter()}
        CURRENT.span, CURRENT.flags = span, flags  # server middleware: this request is the current context
        try:
            status, body = self.routes[self.path](self)
        finally:
            span["end"], CURRENT.span = time.perf_counter(), None
            with LOCK:
                SPANS.append(span)
        self.reply(status, body)


class Gateway(Service):
    name = "gateway"
    routes = {"/checkout": lambda h: (time.sleep(WORK["/checkout"]), traced_call(URL["orders"] + "/create"),
                                      traced_call(URL["payments"] + "/receipt"), (200, {"ok": True}))[-1]}


class Orders(Service):
    name = "orders"
    # the same raw call() as before - it now goes through the propagating middleware
    routes = {"/create": lambda h: (time.sleep(WORK["/create"]), call(URL["payments"] + "/authorize"), (200, {}))[-1]}


class Payments(Service):
    name = "payments"
    routes = {"/authorize": lambda h: (time.sleep(WORK["/authorize"]), (200, {}))[-1],
              "/receipt": lambda h: (time.sleep(WORK["/receipt"]), (200, {}))[-1]}


def run_checkout(services=(Gateway, Orders, Payments), headers=None):
    """Start the three services, send one checkout, stop them. Returns the spans as dicts (times in ms)."""
    SPANS.clear()
    servers = {cls.name: serve(cls) for cls in services}
    URL.update({name: f"http://127.0.0.1:{srv.server_port}" for name, srv in servers.items()})
    call(URL["gateway"] + "/checkout", headers=headers)
    for srv in servers.values():
        srv.shutdown()
        srv.server_close()
    t0 = min(s["start"] for s in SPANS)
    return [{**s, "start": round((s["start"] - t0) * 1000, 1), "end": round((s["end"] - t0) * 1000, 1)} for s in SPANS]


if __name__ == "__main__":
    spans = run_checkout()
    print("spans (JSON lines, one per request):", *(json.dumps(s) for s in sorted(spans, key=lambda s: s["start"])), sep="\n  ")
    for trace_id, members in traces(spans).items():
        print(f"trace {trace_id[:8]}..: {len(members)} span(s):", ", ".join(f"{s['service']} {s['name']}" for s in members))
    root = min((s for s in spans if s["parent_id"] is None), key=lambda s: s["start"])
    print("critical path:", " | ".join(f"{s['service']} {s['name']} self {ms:.0f} ms" for s, ms in critical_path(spans, root)))
    print("trace problems:", *(problems(spans) or ["none"]), sep="\n  ")
