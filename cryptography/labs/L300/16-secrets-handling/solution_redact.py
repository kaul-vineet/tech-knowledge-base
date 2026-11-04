"""Build task solution: a redaction filter on the log HANDLER (so every record passes it), checked by the scanner."""
import copy
import logging

from secrets_app import PATTERNS, SENSITIVE_KEY

MASK = "[REDACTED]"


class RedactingFilter(logging.Filter):
    def __init__(self, known_secrets=()):
        super().__init__()
        self.known = [s for s in known_secrets if s]

    def _clean(self, value, key=""):
        if isinstance(value, dict):
            return {k: self._clean(v, k) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._clean(v, key) for v in value]
        if SENSITIVE_KEY.search(str(key)):
            return MASK  # deny by key name: authorization, password, api_key, ...
        if isinstance(value, str):
            for s in self.known:
                value = value.replace(s, MASK)  # exact values of secrets this process loaded
            for rx in PATTERNS.values():
                value = rx.sub(MASK, value)  # shapes: Bearer tokens, PEM private keys
        return value

    def filter(self, record):
        record.msg = self._clean(record.getMessage())  # message with args already merged
        record.args = None
        if hasattr(record, "ctx"):
            record.ctx = self._clean(copy.deepcopy(record.ctx))  # never mutate the caller's dict
        return True  # keep the record, just cleaned


def install(log: logging.Logger, known_secrets=()) -> logging.Logger:
    for handler in log.handlers:
        handler.addFilter(RedactingFilter(known_secrets))
    return log


def json_logger(stream, name="orders", known_secrets=()):
    from secrets_app import json_logger as base

    return install(base(stream, name), known_secrets)


if __name__ == "__main__":
    import io

    from secrets_app import Secret, handle_request, scan_log

    key, buf = Secret("sk_demo_" + "ab12" * 8), io.StringIO()
    log = json_logger(buf, known_secrets=[key.reveal()])
    handle_request(log, key, 1, debug=True)
    print(buf.getvalue().splitlines()[0])
    print("scanner findings after the fix:", scan_log(buf.getvalue(), known=[key.reveal()]))
