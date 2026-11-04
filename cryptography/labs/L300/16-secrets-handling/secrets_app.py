"""Secrets in an application: load from a file (or env), keep out of repr, JSON logs, a log scanner,
and API-key rotation with a dual-validity window. The request handler below leaks a secret into a log (the fault)."""
import hashlib
import hmac
import io
import json
import logging
import os
import random
import re
import tempfile
from pathlib import Path

SEED = 16
SENSITIVE_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|authorization|cookie)$")  # key names
PATTERNS = {"BEARER": re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{16,}=*"),
            "PRIVATE_KEY": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
            "URL_CREDENTIALS": re.compile(r"://[^/\s:@]+:[^/\s@]+@")}  # user:password@host


class Secret:
    """Holds a secret in a bytearray; repr/str never show it. Python may still keep other copies (see README)."""

    def __init__(self, value: str):
        self._buf = bytearray(value.encode())

    def reveal(self) -> str:
        return self._buf.decode()

    def wipe(self) -> None:
        self._buf[:] = bytes(len(self._buf))  # best effort: overwrites THIS buffer only

    def __repr__(self):
        return "Secret('***')"

    __str__ = __repr__


def load_secret(name: str, env=os.environ) -> Secret:
    """NAME_FILE (a mounted file, e.g. /run/secrets/...) wins over NAME (an env var, visible to child processes)."""
    if env.get(f"{name}_FILE"):
        return Secret(Path(env[f"{name}_FILE"]).read_text(encoding="utf-8").strip())
    if env.get(name):
        return Secret(env[name])
    raise KeyError(f"secret {name} not configured")  # fail closed: no default secret in code


class JsonFormatter(logging.Formatter):
    def format(self, record):  # one JSON object per line: easy to ship, query and scan
        return json.dumps({"level": record.levelname, "msg": record.getMessage(), **getattr(record, "ctx", {})}, sort_keys=True)


def json_logger(stream, name="orders") -> logging.Logger:
    log = logging.getLogger(name)
    log.handlers, log.propagate = [], False
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    return log


def handle_request(log, api_key: Secret, order_id: int, debug: bool) -> None:
    headers = {"Authorization": f"Bearer {api_key.reveal()}", "Accept": "application/json"}
    if debug:  # BUG on purpose: a debug line dumps the outgoing headers, Authorization included
        log.debug("upstream request", extra={"ctx": {"order": order_id, "headers": headers}})
    log.info("order sent", extra={"ctx": {"order": order_id, "status": 200}})


def scan_log(text: str, known=()) -> list:
    """Deterministic leak scanner: [(line_no, kind, detail)]. Tests and the agent-assist lab trust THIS, not a model."""
    found = []
    for n, line in enumerate(text.splitlines(), start=1):
        found += [(n, "KNOWN_SECRET", "value of a configured secret") for s in known if s and s in line]
        found += [(n, kind, "pattern") for kind, rx in PATTERNS.items() if rx.search(line)]
        for key, value in re.findall(r'"?([\w-]+)"?\s*[:=]\s*"?([^",}\s]+)', line):
            if SENSITIVE_KEY.search(key) and value not in ("[REDACTED]", "null", "") and not value.isdigit():
                found.append((n, "SENSITIVE_KEY", key))
    return sorted(set(found))


class ApiKeys:
    """Server side of a rotation: stores only SHA-256 hashes; the previous key works until grace_until."""

    def __init__(self, key: str):
        self.current, self.previous, self.grace_until = self._h(key), None, 0

    @staticmethod
    def _h(key: str) -> bytes:
        return hashlib.sha256(key.encode()).digest()

    def rotate(self, new_key: str, now: float, grace_s: float) -> None:
        self.previous, self.current, self.grace_until = self.current, self._h(new_key), now + grace_s

    def check(self, presented: str, now: float):
        h = self._h(presented)
        if hmac.compare_digest(h, self.current):  # constant-time compare of fixed-length hashes
            return "current"
        if self.previous and now <= self.grace_until and hmac.compare_digest(h, self.previous):
            return "previous"  # log this: when it drops to zero, clients have migrated
        return None


if __name__ == "__main__":
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "orders_api_key"
        f.write_text("sk_demo_" + "".join(rng.choice("abcdef0123456789") for _ in range(32)) + "\n", encoding="utf-8")
        key = load_secret("ORDERS_API_KEY", env={"ORDERS_API_KEY_FILE": str(f)})
    print("loaded from file:", key, "| length", len(key.reveal()))
    buf = io.StringIO()
    log = json_logger(buf)
    debug_order = rng.randint(1, 5)  # seeded fault: the same request takes the debug path on every run
    for order in range(1, 6):
        handle_request(log, key, order, debug=order == debug_order)
    lines = buf.getvalue().splitlines()
    print(f"{len(lines)} JSON log lines, e.g. {lines[0]}")
    print("scanner findings:")
    for n, kind, detail in scan_log(buf.getvalue(), known=[key.reveal()]):
        print(f"  line {n}: {kind} ({detail})")
