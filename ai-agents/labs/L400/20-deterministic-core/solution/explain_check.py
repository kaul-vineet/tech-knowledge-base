"""Solution (lesson 20 build task): an explanation is shown only if code can verify it matches the decision."""
import re

WORDS = {"approve_auto": r"approv", "escalate": r"escalat|person|review", "deny": r"den(y|ied)|declin"}


def template(decision):
    return f"Decision: {decision['action']} for {decision['amount']}. Reason: {decision['rule']}."


def checked(text, decision):
    if not text or len(text) > 400:
        return template(decision)
    low = text.lower()
    if not re.search(WORDS[decision["action"]], low):
        return template(decision)  # the decided action must be named
    if any(re.search(p, low) for a, p in WORDS.items() if a != decision["action"]):
        return template(decision)  # ...and no other action
    numbers = {float(n) for n in re.findall(r"\d+(?:\.\d+)?", text)}
    allowed = {float(decision["amount"])} | {float(n) for n in re.findall(r"\d+", decision["rule"])}
    return text if numbers <= allowed else template(decision)  # no invented amounts
