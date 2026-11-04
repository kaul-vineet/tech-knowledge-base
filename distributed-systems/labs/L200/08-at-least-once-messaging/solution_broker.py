"""SOLUTION for the lesson 8 build task (python solution_broker.py): broker.py + an idempotent consumer.
L200 lesson 8 (python broker.py): a tiny at-least-once broker over HTTP. /receive hides a message for a
visibility timeout, /ack deletes it, no ack = redelivery, too many receives = dead-letter queue (DLQ).
Two consumers crash mid-work (seeded); the ledger shows the duplicates at-least-once delivery creates."""
import random, threading

from helpers import QuietHandler, SimClock, call, serve

VISIBILITY, MAX_RECEIVES = 3.0, 3  # hide a received message for 3 s; dead-letter after 3 unacked receives


class Broker(QuietHandler):
    clock, lock, queue, dlq, seq = SimClock(), threading.Lock(), [], [], 0

    @classmethod
    def reset(cls, clock):
        cls.clock, cls.queue, cls.dlq, cls.seq = clock, [], [], 0

    def do_POST(self):
        req, cls, now = self.read_json(), type(self), self.clock()
        with self.lock:
            if self.path == "/send":
                cls.seq += 1
                cls.queue.append({"id": f"m{cls.seq}", "body": req["body"], "visible_at": now, "receives": 0})
                return self.reply(200, {"id": f"m{cls.seq}"})
            if self.path == "/receive":
                for m in list(cls.queue):
                    if m["visible_at"] > now:  # in flight: invisible until its visibility timeout ends
                        continue
                    if m["receives"] >= MAX_RECEIVES:  # poison: received N times, never acked -> DLQ
                        cls.queue.remove(m)
                        cls.dlq.append(m)
                        continue
                    m["receives"] += 1
                    m["visible_at"] = now + VISIBILITY  # lease on the message, not a delete
                    m["receipt"] = f"{m['id']}#{m['receives']}"  # new receipt for every delivery
                    return self.reply(200, {k: m[k] for k in ("id", "body", "receipt", "receives")})
                return self.reply(404, {"empty": True, "in_flight": len(cls.queue)})
            m = next((m for m in cls.queue if m.get("receipt") == req["receipt"]), None)
            if m is None:  # /ack with an old receipt: the message was redelivered (or already acked)
                return self.reply(409, {"error": "stale receipt"})
            cls.queue.remove(m)  # ack = done: delete for good
            self.reply(200, {"acked": m["id"]})


def consume(name, url, rng, ledger, log, crash_rate):
    status, msg, _ = call(url + "/receive", {})
    if status != 200:
        return
    if msg["body"] == "poison":  # a payload the handler can never process: it crashes every time
        return log(f"{name} {msg['id']}={msg['body']} receive #{msg['receives']}: CRASHED while parsing")
    if any(i == msg["id"] for i, _ in ledger):  # idempotent consumer: this message id was already charged
        call(url + "/ack", {"receipt": msg["receipt"]})  # (real DB: unique key on message id, same transaction)
        return log(f"{name} {msg['id']}={msg['body']} receive #{msg['receives']}: duplicate -> skipped, acked")
    ledger.append((msg["id"], msg["body"]))  # the side effect (e.g. charge a card) happens first ...
    if rng.random() < crash_rate:  # ... then the consumer crashes mid-work: no ack -> redelivery later
        return log(f"{name} {msg['id']}={msg['body']} receive #{msg['receives']}: charged, CRASHED before ack")
    call(url + "/ack", {"receipt": msg["receipt"]})
    log(f"{name} {msg['id']}={msg['body']} receive #{msg['receives']}: charged, acked")


def run(bodies=("o1", "o2", "o3", "o4", "o5", "o6", "poison"), crash_rate=0.3, seed=9, quiet=False):
    clock, ledger, rng, lines = SimClock(), [], random.Random(seed), []
    Broker.reset(clock)
    srv = serve(Broker)
    url = f"http://127.0.0.1:{srv.server_port}"
    for body in bodies:
        call(url + "/send", {"body": body})
    while Broker.queue and clock() < 60:  # one tick = 1 simulated second
        for name in ("c1", "c2"):
            consume(name, url, rng, ledger, lambda s: lines.append(f"t={clock():.0f} {s}"), crash_rate)
        clock.advance(1.0)
    srv.shutdown()
    srv.server_close()
    if not quiet:
        print("\n".join(lines))
    return {"log": lines, "ledger": ledger, "dlq": [m["body"] for m in Broker.dlq]}


if __name__ == "__main__":
    out = run()
    ids = [i for i, _ in out["ledger"]]
    print(f"ledger: {len(ids)} charges for {len(set(ids))} orders -> {len(ids) - len(set(ids))} duplicates")
    print("dead-letter queue:", out["dlq"])
