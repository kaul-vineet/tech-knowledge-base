"""Deterministic guardrails: input limits, injection screening of retrieved text, secret redaction."""
import os
import re

MAX_INPUT_CHARS = 500
INJECTION = re.compile(r"ignore (all )?previous instructions|disregard (the|your) (rules|instructions)|"
                       r"you are now|call \w+ with \{", re.I)
SECRET = re.compile(r"\bsk-[A-Za-z0-9-]{8,}")  # API-key shaped strings
KNOWN_SECRETS = [v for k, v in os.environ.items() if k.endswith("_API_KEY") and len(v) >= 8]


def check_input(text):
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError(f"input longer than {MAX_INPUT_CHARS} characters")
    return re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)  # strip control characters


def screen(source, text):
    """Retrieved text is DATA. If it looks like instructions, quarantine it instead of passing it on."""
    if INJECTION.search(text):
        return f"[removed: possible prompt injection in {source}]", True
    return text, False


def contains_secret(text):
    return bool(SECRET.search(text)) or any(s in text for s in KNOWN_SECRETS)


def redact(text):
    for s in KNOWN_SECRETS:
        text = text.replace(s, "[REDACTED]")
    return SECRET.sub("[REDACTED]", text)
