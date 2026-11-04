"""L200 lesson 11 (python ratelimit.py): per-client token buckets in an HTTP API. Over the limit the server
answers 429 Too Many Requests + Retry-After (RFC 6585 / RFC 9110). A polite client waits as told, a naive
one retries every 0.1 s, a quiet one is never affected. Simulated clock: identical output on every run."""
import math
from email.utils import parsedate_to_datetime

from helpers import QuietHandler, SimClock, call, serve

RATE, BURST = 2.0, 5  # per client: 2 requests/s on average, bursts of up to 5


class TokenBucket:
    def __init__(self, rate, burst, clock):
        self.rate, self.burst, self.clock = rate, burst, clock
        self.tokens, self.last = float(burst), clock()

    def allow(self):  # returns (allowed, seconds until a token is available)
        now = self.clock()
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)  # refill for elapsed time
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True, 0.0
        return False, (1 - self.tokens) / self.rate


class Api(QuietHandler):
    clock, limiters, make_limiter = SimClock(), {}, None

    def do_GET(self):
        client = self.headers.get("X-Client-Id", self.client_address[0])  # per-client limit key
        limiter = self.limiters.setdefault(client, (type(self).make_limiter or default_limiter)(self.clock))
        ok, wait = limiter.allow()
        if ok:
            return self.reply(200, {"ok": True})
        # 429 + Retry-After in whole seconds (delay-seconds form), rounded UP so an early retry can't fail
        self.reply(429, {"error": "too many requests"}, {"Retry-After": str(max(1, math.ceil(wait)))})


def default_limiter(clock):
    return TokenBucket(RATE, BURST, clock)


def retry_after_seconds(value, now_epoch=0.0):  # RFC 9110 allows delay-seconds OR an HTTP-date
    if value.strip().isdigit():
        return int(value)
    return max(0.0, parsedate_to_datetime(value).timestamp() - now_epoch)


def run(clients, make_limiter=None):
    """clients: {name: (requests_wanted, honor_retry_after)}. Event loop on a simulated clock."""
    clock = SimClock()
    Api.clock, Api.limiters, Api.make_limiter = clock, {}, make_limiter
    srv = serve(Api)
    url = f"http://127.0.0.1:{srv.server_port}/data"
    state = {n: {"next": 0.0, "ok": 0, "429": 0, "trace": [], "want": w, "honor": h} for n, (w, h) in clients.items()}
    while active := [n for n, s in state.items() if s["ok"] < s["want"]]:
        name = min(active, key=lambda n: (state[n]["next"], n))  # next event in time order
        s = state[name]
        clock.t = s["next"]
        status, _, headers = call(url, headers={"X-Client-Id": name})
        if status == 200:
            s["ok"] += 1
            s["trace"].append("200")
            s["done"] = clock.t
        else:
            s["429"] += 1
            wait = retry_after_seconds(headers["Retry-After"]) if s["honor"] else 0.1  # naive: hammer again
            s["trace"].append(f"429(wait {wait:g})")
            s["next"] = round(clock.t + wait, 3)
    srv.shutdown()
    srv.server_close()
    return state


if __name__ == "__main__":
    out = run({"alice": (12, True), "bob": (12, False), "carol": (3, True)})
    print("alice trace:", " ".join(out["alice"]["trace"]))
    for name, s in out.items():
        print(f"{name:<5} ({'honors Retry-After' if s['honor'] else 'retries every 0.1 s'}): "
              f"{s['ok']} ok, {s['429']} x 429, done at t={s['done']:g}s")
