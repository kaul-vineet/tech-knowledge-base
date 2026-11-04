"""Lab 21 - deterministic alarm rules at the gateway. The ONLY place alarms come from.

decide(snapshot, previous) -> list of alarms, each {"name", "dev", "value", "limit"}:
  TEMP_HIGH     a board's newest reading >= 30 C; stays raised until it is below 28 C (hysteresis,
                the same thresholds as firmware_alarm.py on the board)
  DRIFT_LAT/TEMP  copied from the digital twin's CUSUM check (lab 20)
  AUTH_REJECTS  the gateway rejected radio frames on MAC or replay (lab 19) in this window
freeze(alarms) -> (JSON text, SHA-256): the record the operator sees; nothing after decide() may
change it, and the digest proves it did not.
"""
import hashlib
import json

TEMP_HIGH_C, TEMP_CLEAR_C = 30, 28


def decide(snapshot, previous=()):
    was_hot = set(a["dev"] for a in previous if a["name"] == "TEMP_HIGH")
    out = []
    for d in snapshot["devices"]:
        t = d["temps"][-1]
        if t >= TEMP_HIGH_C or (d["dev"] in was_hot and t >= TEMP_CLEAR_C):
            out.append({"name": "TEMP_HIGH", "dev": d["dev"], "value": t, "limit": TEMP_HIGH_C})
    for a in snapshot.get("twin_alarms", []):
        out.append({"name": a["alarm"], "dev": a["dev"], "value": a["z"], "limit": None})
    rejects = snapshot.get("auth", {})
    n = rejects.get("mac", 0) + rejects.get("replay", 0)
    if n:
        out.append({"name": "AUTH_REJECTS", "dev": "gateway", "value": n, "limit": 0})
    return sorted(out, key=lambda a: (a["name"], a["dev"]))


def freeze(alarms):
    text = json.dumps(alarms, sort_keys=True)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
