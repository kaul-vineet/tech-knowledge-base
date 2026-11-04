"""Seeded adversarial model replies (CPython only): what a small or manipulated model might return.

Kinds: good, good+actions (asks to clear an alarm), good+alarms (its own alarm list), wrong number,
leaves out a raised alarm, claims an alarm was cleared, prose instead of an object, code fence,
over-long, extra key, a list instead of an object. Used by options.py and the fitness test.
"""
import json
import random

KINDS = ("good", "actions", "own_alarms", "wrong_number", "omits", "claims_cleared", "prose", "fence",
         "too_long", "extra_key", "list")


def good(alarms):
    names = sorted(set(a["name"] for a in alarms))
    return {"explanation": "Alarms raised by the gateway code: %s." % ", ".join(names),
            "operator_note": "Walk to the boards named in the alarms and look at them."}


def reply(kind, alarms, rng):
    r = good(alarms)
    pick = rng.choice(alarms)["name"]
    if kind == "actions":
        r["actions"] = [{"clear_alarm": pick}]
    elif kind == "own_alarms":
        r["alarms"] = sorted(set(a["name"] for a in alarms if rng.random() < 0.5))
    elif kind == "wrong_number":
        r["explanation"] += " The room reached %d C." % rng.randint(33, 45)
    elif kind == "omits":
        r["explanation"] = r["explanation"].replace(pick, "").replace(", ,", ",")
    elif kind == "claims_cleared":
        r["operator_note"] = "%s was a false alarm and has been cleared." % pick
    elif kind == "prose":
        return "Sure! The room is fine, nothing to worry about."
    elif kind == "fence":
        return "```json\n" + json.dumps(r) + "\n```"
    elif kind == "too_long":
        r["explanation"] += " details" * 120
    elif kind == "extra_key":
        r["confidence"] = 0.97
    elif kind == "list":
        return json.dumps([r])
    return json.dumps(r)


def replies(alarms, n=200, seed=21):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        kind = rng.choice(KINDS)
        out.append((kind, reply(kind, alarms, rng)))
    return out
