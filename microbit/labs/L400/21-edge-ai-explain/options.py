"""Lab 21 design options, measured: who may change an alarm? (prints JSON lines)

A  the model decides the alarm list            (alarms := the model's own "alarms" list)
B  the model may act on alarms (BEFORE)         (code's alarms, then the model's "actions" applied)
C  explain only, read-only record, checked text (solution.py)
Each option sees 200 seeded adversarial replies (fuzz.py) and the injected-label incident through
the fake model server. Counted: replies after which the alarms differ from what the code decided.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fuzz  # noqa: E402
import incident_assistant as before  # noqa: E402
import solution  # noqa: E402
from alarms import decide  # noqa: E402

NAMES = set(solution.NAMES)


def model_decides(text, code_alarms):
    try:
        own = json.loads(text).get("alarms")
    except (ValueError, AttributeError):
        own = None
    names = set(own) & NAMES if isinstance(own, list) else set()
    return [a for a in code_alarms if a["name"] in names]


def model_acts(text, snapshot):
    try:
        return before.run(lambda m: text, snapshot)["alarms"]
    except (ValueError, AttributeError, TypeError):
        return decide(snapshot)           # crashed: the gateway keeps its own alarms (best case)


def measure(snapshot, chat_text=None):
    code = decide(snapshot)
    fz = fuzz.replies(code)
    rows = {"A model decides": 0, "B model may act": 0, "C explain only": 0}
    accepted = 0
    for _, text in fz:
        rows["A model decides"] += model_decides(text, code) != code
        rows["B model may act"] += model_acts(text, snapshot) != code
        out = solution.run(lambda m: text, snapshot)
        rows["C explain only"] += out["alarms"] != code
        accepted += out["accepted"]
    return rows, accepted, len(fz)


def injection(snapshot):
    """The injected-label incident through the fake model server: which alarms survive per option?"""
    from local_agent import fake_model_server
    from local_agent.client import chat
    server, url = fake_model_server.start_in_thread()
    try:
        ask = lambda m: chat(m, base_url=url, model="fake-model", timeout=60)   # noqa: E731
        code = decide(snapshot)
        text = ask(before.build_messages(snapshot, code))
        res = {"A model decides": model_decides(text, code), "B model may act": model_acts(text, snapshot),
               "C explain only": solution.run(ask, snapshot)["alarms"]}
    finally:
        server.shutdown()
        server.server_close()
    return dict((k, "TEMP_HIGH" in [a["name"] for a in v]) for k, v in res.items())


if __name__ == "__main__":
    snap = before.incident.snapshot()
    print(json.dumps({"injected_label_temp_high_still_raised": injection(snap)}))
    rows, accepted, n = measure(snap)
    for k, v in rows.items():
        print(json.dumps({"option": k, "alarm_sets_changed": v, "of": n}))
    print(json.dumps({"option": "C explain only", "replies_published": accepted, "fallback_notes": n - accepted}))
