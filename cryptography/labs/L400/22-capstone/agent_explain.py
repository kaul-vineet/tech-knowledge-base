"""Agent assist (capstone): a local model EXPLAINS audit anomalies; the rules in audit.py DECIDE them.
Only the anomaly lines leave the service (rule, sequence number, user pseudonym) - never key material, wrapped keys or
document content; lesson 16's scanner and lesson 9's secret regex gate the prompt. Explanations for anomaly ids the
rules did not report are REJECTED; anomalies the model skipped stay reported."""
import importlib.util
import re
import sys

import paths  # noqa: F401
from local_agent import fake_model_server
from local_agent.client import chat
from secrets_app import scan_log

_spec = importlib.util.spec_from_file_location("l200_agent_assist", paths.LABS / "L200" / "09-local-ca" / "agent_assist.py")
_l200 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_l200)
SECRET_GATE = _l200.SECRET
SYSTEM = ("You explain security audit anomalies to an on-call engineer in one sentence each. "
          "Answer one line per anomaly: 'EXPLAIN <id>: <explanation>'. Do not invent anomalies.")


def prompt_for(anomalies: list) -> str:
    text = "\n".join(f"ANOMALY {a['id']} {a['rule']}: seq {a['seq']} - {a['summary']}" for a in anomalies)
    if scan_log(text) or SECRET_GATE.search(text):
        raise ValueError("refusing to send: secret-like content in the anomaly summary")
    return f"[[AUDIT-EXPLAIN]] Explain these anomalies:\n<anomalies>{text}</anomalies>"


def explain(anomalies: list, real: bool = False) -> list:
    server, base_url, model = None, None, None
    if not real:
        server, base_url = fake_model_server.start_in_thread()
        model = fake_model_server.MODEL_ID
    try:
        reply = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt_for(anomalies)}],
                     base_url=base_url, model=model)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    known = {a["id"]: a for a in anomalies}
    claims = dict(re.findall(r"EXPLAIN (\w+): (.*)", reply))
    rows = [{"id": i, "verdict": "ACCEPTED" if i in known else "REJECTED (no such anomaly)", "text": t[:80]} for i, t in claims.items()]
    rows += [{"id": i, "verdict": "UNEXPLAINED (still reported by the rules)", "text": ""} for i in known if i not in claims]
    return rows


if __name__ == "__main__":
    demo = [{"id": "A1", "rule": "unwrap_burst", "seq": 30, "summary": "mallory: 6 unwraps in 60 s"}]
    for row in explain(demo, real="--real" in sys.argv):
        print(row)
