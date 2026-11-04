"""Agent assist: a local model PROPOSES threats for the model's elements; deterministic code DECIDES what each
proposal is worth. Only element names and flows are sent (never keys, logs or secrets; lesson 9's secret gate checks).
Verdicts: CONFIRMED (element + STRIDE letter valid, control exists and its tests exist), GAP (valid threat, no control:
triage it), REJECTED (unknown element, STRIDE letter that does not apply, or an invented control).
Default: deterministic fake model server. --real: Ollama/llama.cpp at LOCAL_MODEL_URL / LOCAL_MODEL."""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent
sys.path.append(str(HERE.parents[1] / "L200" / "09-local-ca"))
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

import solution_verified as sv  # noqa: E402
import threat_model as tm  # noqa: E402

_spec = importlib.util.spec_from_file_location("l200_agent_assist", HERE.parents[1] / "L200" / "09-local-ca" / "agent_assist.py")
_l200 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_l200)
SECRET_GATE = _l200.SECRET
SYSTEM = ("You are a threat-modelling assistant. For the data-flow elements given, propose threats using STRIDE. "
          "Answer one per line: 'THREAT <element> <S|T|R|I|D|E>: <threat> | CONTROL <control id or NONE>'.")
LINE = re.compile(r"THREAT (\S+) ([STRIDE]): (.*?) \| CONTROL (\S+)")


def prompt_for(model) -> str:
    text = "\n".join(f"{n} ({e['type']}, zone {e.get('zone', e.get('from', '') + '->' + e.get('to', ''))})" for n, e in model["elements"].items())
    text += "\nknown controls: " + ", ".join(sorted(model["controls"]))
    if SECRET_GATE.search(text):
        raise ValueError("refusing to send: secret-like content in the prompt")
    return f"[[THREAT-PROPOSE]] Propose threats for:\n<model>{text}</model>"


def judge(model, proposal) -> str:
    el, stride, _, control = proposal
    e = model["elements"].get(el)
    if e is None:
        return "REJECTED - unknown element"
    if stride not in tm.APPLIES[e["type"]]:
        return f"REJECTED - {stride} does not apply to a {e['type']}"
    if control == "NONE":
        return "GAP - valid threat with no control: triage it (not added automatically)"
    if control not in model["controls"]:
        return f"REJECTED - control {control} does not exist"
    if control not in sv.verified_controls(model):
        return f"REJECTED - control {control} has no existing test"
    return f"CONFIRMED - {control} proven by {model['controls'][control]['tests'][0].split('::', 1)[1]}"


def review(model, base_url=None, model_name=None) -> list:
    reply = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt_for(model)}],
                 base_url=base_url, model=model_name)
    return [(p, judge(model, p)) for p in LINE.findall(reply)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use LOCAL_MODEL_URL / LOCAL_MODEL (e.g. Ollama)")
    args = ap.parse_args(argv)
    server, base_url, name = None, None, None
    if not args.real:
        server, base_url = fake_model_server.start_in_thread()
        name = fake_model_server.MODEL_ID
    try:
        rows = review(tm.load(), base_url, name)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    for (el, stride, what, control), verdict in rows:
        print(f"{el} {stride} ({what[:40]}) -> {verdict}")
    counts = {k: sum(v.startswith(k) for _, v in rows) for k in ("CONFIRMED", "GAP", "REJECTED")}
    print(f"verdicts {counts}; the model only proposes - the checker decides, and nothing is merged automatically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
