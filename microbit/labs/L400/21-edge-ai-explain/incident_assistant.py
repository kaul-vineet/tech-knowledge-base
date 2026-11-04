"""Lab 21 - local model at the gateway explains incidents and drafts the operator note (BEFORE).

Pattern from the LPC1768 guide's capstone: deterministic code raises the alarms; a local model
(Ollama on the Mac mini / Windows PC, OpenAI-compatible) explains them in plain language.
This first version trusts the model too much: it parses the reply and APPLIES any "actions" in it,
so the model - or text hidden in the data it reads - can clear an alarm the code raised.

Run:  python incident_assistant.py --fake      (deterministic fake model server, no download)
      python incident_assistant.py             (real local model: LOCAL_MODEL_URL / LOCAL_MODEL)
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "_shared"))
sys.path.insert(0, str(HERE))
import alarms as rules  # noqa: E402
import incident  # noqa: E402
from local_agent.client import chat  # noqa: E402

SYSTEM = ("You explain incidents of a classroom micro:bit sensor network to the teacher in 2-4 plain "
          "sentences. Reply only with an object {\"explanation\": \"...\", \"operator_note\": \"...\"}.")


def build_messages(snapshot, alarms):
    data = json.dumps({"alarms": alarms, "devices": snapshot["devices"]}, sort_keys=True)
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "[[MICROBIT-INCIDENT]] Explain this incident:\n<incident>" + data + "</incident>"}]


def run(chat_fn, snapshot):
    alarms = rules.decide(snapshot)
    reply = json.loads(chat_fn(build_messages(snapshot, alarms)))
    for action in reply.get("actions", []):           # the model gets a WRITE path to the alarms
        if "clear_alarm" in action:
            alarms = [a for a in alarms if a["name"] != action["clear_alarm"]]
    return {"alarms": alarms, "explanation": reply.get("explanation", ""), "note": reply.get("operator_note", "")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args(argv)
    server = None
    if args.fake:
        from local_agent import fake_model_server
        server, url = fake_model_server.start_in_thread()
        chat_fn = lambda m: chat(m, base_url=url, model="fake-model", timeout=60)   # noqa: E731
    else:
        chat_fn = lambda m: chat(m, timeout=120)                                      # noqa: E731
    try:
        out = run(chat_fn, incident.snapshot())
        print("alarms shown:", ", ".join("%s@%s" % (a["name"], a["dev"]) for a in out["alarms"]))
        print("operator note:", out["note"])
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
