"""L100 (python idempotency.py): retries + lost responses = duplicate charges. Fix: Idempotency-Key
header + server-side dedupe store -> exactly-once *effect* over at-least-once delivery. Seeded."""
import hashlib, json, random, re, threading, urllib.request, uuid
from urllib.error import HTTPError, URLError

from helpers import OPENER, QuietHandler, serve  # plumbing: quiet handler, reply(), server thread

KEY_RE = re.compile(r'^"([0-9a-f-]{36})"$')  # our published key format: quoted UUID string


class PaymentB(QuietHandler):
    enforce = False          # True -> require Idempotency-Key and dedupe
    ledger, store, lock = [], {}, threading.Lock()  # store = dedupe store: key -> fp/state/response
    rng, loss_rate = random.Random(3), 0.4  # seeded: which responses get "lost" on the network

    def do_POST(self):
        raw = self.read_body()
        fingerprint, key = hashlib.sha256(raw).hexdigest(), self.headers.get("Idempotency-Key")
        if self.enforce:
            if not (m := KEY_RE.match(key or "")):  # key missing/malformed -> 400
                return self.reply(400, {"title": "Idempotency-Key is missing or malformed"})
            key = m.group(1)
            with self.lock:
                seen = self.store.get(key)
                if seen and seen["fp"] != fingerprint:  # same key, different payload -> 422
                    return self.reply(422, {"title": "Idempotency-Key is already used"})
                if seen and seen["state"] == "in-progress":  # original still running -> 409
                    return self.reply(409, {"title": "A request is outstanding for this key"})
                if seen:  # retry of a completed request: replay the stored response, no new charge
                    return self.reply(*seen["response"])
                self.store[key] = {"fp": fingerprint, "state": "in-progress"}  # first time
        with self.lock:  # the side effect: money moves
            self.ledger.append(json.loads(raw)["amount"])
            response = (201, {"charge_id": f"ch_{len(self.ledger)}"})
            if self.enforce:  # same lock as the charge: no window where a crash could duplicate
                self.store[key].update(state="done", response=response)
            lose_it = self.rng.random() < self.loss_rate
        if lose_it:  # lost response: charge committed, client never hears back -> outcome unknown
            self.close_connection = True
            return
        self.reply(*response)


def pay(url, amount, key=None, max_attempts=5):
    """At-least-once client: resend the SAME request (and SAME key) until it gets an answer."""
    headers = {"Content-Type": "application/json"}
    if key:  # one key per logical operation, created by the caller BEFORE this retry loop
        headers["Idempotency-Key"] = f'"{key}"'  # sf-string per the IETF draft
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(url, json.dumps({"amount": amount}).encode(), headers)
        try:
            with OPENER.open(req, timeout=2) as r:
                return r.status, json.load(r), attempt
        except HTTPError as e:
            return e.code, json.load(e), attempt
        except (URLError, ConnectionError):  # no response -> unknown outcome -> retry
            continue
    return None, None, max_attempts


def run(enforce, seed=1):
    PaymentB.enforce, PaymentB.rng = enforce, random.Random(3)
    PaymentB.ledger.clear(); PaymentB.store.clear()
    srv = serve(PaymentB)
    url, keys = f"http://127.0.0.1:{srv.server_port}/charges", random.Random(seed)
    print(f"--- Idempotency-Key {'ON' if enforce else 'OFF'}: 5 orders x 10 ---")
    for order in range(1, 6):
        # Production: uuid.uuid4(). Seeded here only so the output is reproducible.
        key = str(uuid.UUID(int=keys.getrandbits(128), version=4)) if enforce else None
        status, body, attempts = pay(url, 10, key)
        print(f"order {order}: {status} {body} after {attempts} attempt(s)")
    print(f"ledger: {len(PaymentB.ledger)} charges, total {sum(PaymentB.ledger)} (expected 50)")
    if enforce:
        print("reuse key with amount 99 ->", pay(url, 99, key)[:2])
        print("no key at all            ->", pay(url, 10)[:2])
    srv.shutdown(); srv.server_close()


if __name__ == "__main__":
    run(enforce=False)
    run(enforce=True)
