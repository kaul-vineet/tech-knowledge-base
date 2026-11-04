"""L100: service A calls service B over HTTP (request/response) and measures latency.

python two_services.py   # starts B on a free localhost port, A sends 5 requests + 1 bad one
"""
import json, statistics, time
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from helpers import OPENER, QuietHandler, serve  # plumbing: quiet handler, reply(), server thread

PRICES = {"apple": 3, "pear": 4, "plum": 5}


class ServiceB(QuietHandler):
    """Service B: GET /price?item=apple -> 200 {"item": "apple", "price": 3}; unknown -> 404."""
    def do_GET(self):  # request message in (method + target) -> one response message out
        item = parse_qs(urlsplit(self.path).query).get("item", [""])[0]
        if item in PRICES:
            self.reply(200, {"item": item, "price": PRICES[item]})  # 2xx = success
        else:
            self.reply(404, {"error": f"unknown item {item!r}"})  # 4xx = client asked wrongly


def start_b(port=0):  # port 0 = let the OS pick a free port
    return serve(ServiceB, port)


def call_b(base_url, item, timeout=2.0):
    """Service A's side (the RPC stub): one request, one response. Returns (json, latency_ms)."""
    t0 = time.perf_counter()  # latency: monotonic clock, can't jump back like time.time()
    with OPENER.open(f"{base_url}/price?item={item}", timeout=timeout) as resp:  # always a timeout
        data = json.load(resp)  # marshalling: JSON bytes on the wire -> Python dict
    return data, (time.perf_counter() - t0) * 1000


def main():
    b = start_b()
    url = f"http://127.0.0.1:{b.server_port}"
    print(f"service B listening on {url}")
    latencies = []
    for item in ["apple", "pear", "plum", "apple", "pear"]:
        data, ms = call_b(url, item)
        latencies.append(ms)
        print(f"A -> B  GET /price?item={item:<5} -> 200 {data}  ({ms:.1f} ms)")
    try:
        call_b(url, "kiwi")
    except HTTPError as e:  # errors are results: urllib raises non-2xx; handle 404 as an outcome
        print(f"A -> B  GET /price?item=kiwi  -> {e.code} {json.load(e)}")
    print(f"latency ms: min={min(latencies):.1f} median={statistics.median(latencies):.1f} "
          f"max={max(latencies):.1f}")  # median, not mean: a few slow calls skew the average
    b.shutdown()


if __name__ == "__main__":
    main()
