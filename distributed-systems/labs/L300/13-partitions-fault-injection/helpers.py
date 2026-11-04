"""Plumbing for lab 13 (not the lesson's concept): the lease store from lesson 7 (TTL + compare-and-set, a
token that grows with every new holder), in-process and on simulated ticks so the proxy can cut it off
deterministically, plus the JSON-lines history writer."""
import json


class LeaseStore:
    def __init__(self):
        self.holder, self.token, self.expires = None, 0, 0.0

    def acquire(self, name, now, ttl):
        if self.holder is None or now >= self.expires:  # free or expired: the next holder gets a HIGHER token
            self.holder, self.token, self.expires = name, self.token + 1, now + ttl
            return True, self.token
        return False, self.token

    def renew(self, name, token, now, ttl):
        if self.holder == name and self.token == token and now < self.expires:
            self.expires = now + ttl
            return True
        return False


def jsonl(history):
    """Jepsen-style history: one invoke and one completion line per operation (type ok / fail)."""
    lines = []
    for op in sorted(history, key=lambda o: o["start"]):
        lines.append({"time": op["start"], "process": op["process"], "type": "invoke", "f": op["f"],
                      "value": op["value"] if op["f"] == "write" else None, "node": op["node"]})
    for op in sorted(history, key=lambda o: o["end"]):
        lines.append({"time": op["end"], "process": op["process"], "type": "ok" if op["ok"] else "fail",
                      "f": op["f"], "value": op["value"], "node": op["node"], **({"error": op["error"]} if "error" in op else {})})
    return [json.dumps(line) for line in sorted(lines, key=lambda l: l["time"])]
