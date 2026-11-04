"""L100: a slow service B; A without a timeout waits as long as B takes, A with one fails fast.

python timeouts.py
"""
import math, random, statistics, time
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit

from helpers import OPENER, QuietHandler, serve  # plumbing: quiet handler, reply(), server thread


class SlowB(QuietHandler):
    """GET /work?delay=2.0 -> sleeps `delay` seconds, then answers 200 ok."""
    def do_GET(self):
        time.sleep(float(parse_qs(urlsplit(self.path).query).get("delay", ["0"])[0]))
        try:  # a client timeout does NOT stop the server: B finishes the work anyway
            self.reply(200, b"ok")
        except OSError:
            pass  # client already gave up and closed the socket


def start_b():
    return serve(SlowB)


def call(url, timeout=None):
    """timeout=None -> no client timeout (blocks until B answers, possibly forever)."""
    t0 = time.perf_counter()
    try:
        kwargs = {} if timeout is None else {"timeout": timeout}  # timeout = max wait per socket op
        with OPENER.open(url, **kwargs) as r:
            return f"{r.status} {r.read().decode()}", time.perf_counter() - t0
    except (TimeoutError, URLError) as e:  # fail fast. read: TimeoutError, connect: URLError
        return f"FAILED {type(e).__name__}", time.perf_counter() - t0


def choose_timeout(seed=7, false_timeout_rate=0.001):
    """Pick the value from data: the latency percentile matching an acceptable false-timeout
    rate (0.1% -> p99.9)."""
    rng = random.Random(seed)  # stand-in for B's measured latencies: lognormal around 40 ms
    samples = [rng.lognormvariate(math.log(0.040), 0.35) for _ in range(10_000)]
    q = statistics.quantiles(samples, n=1000)  # q[i] = p((i+1)/10), e.g. q[998] = p99.9
    print(f"B latency: p50={q[499]*1000:.0f} ms  p99={q[989]*1000:.0f} ms  p99.9={q[998]*1000:.0f} ms")
    return round(q[round((1 - false_timeout_rate) * 1000) - 1], 3)


def main():
    b = start_b()
    url = f"http://127.0.0.1:{b.server_port}/work?delay=2.0"
    print("B takes 2.0 s to answer.")
    for timeout in (None, 0.5):
        result, took = call(url, timeout)
        print(f"A timeout={str(timeout):<4} -> {result:<20} after {took:.1f} s")
    print(f"suggested timeout for A->B: {choose_timeout()} s")
    b.shutdown()


if __name__ == "__main__":
    main()
