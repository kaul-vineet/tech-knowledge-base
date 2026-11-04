"""Agent assist (lesson 21): the model drafts the Context paragraph of the upgrade record; code checks every number
against the measured report and decides nothing. A draft with an unknown number is dropped (code text is used)."""
import json
import re
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import governance  # noqa: E402


def ask(prompt, base_url, model):
    try:
        r = requests.post(f"{base_url}/chat/completions", timeout=30, json={
            "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0})
        return r.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, ValueError):
        return None


def unknown_numbers(text, report):
    allowed = set(re.findall(r"\d+(?:\.\d+)?", json.dumps(report)))
    allowed |= {str(len(report["regressions"])), f"{report['pass_rate'] * 100:.0f}"}
    return [n for n in re.findall(r"\d+(?:\.\d+)?", text or "") if n not in allowed]


def assisted_record(report, ask_fn):
    draft = ask_fn("Draft the Context paragraph of a model-upgrade decision record. Restate only these numbers.\n"
                   f"<adr_draft>{json.dumps(report)}</adr_draft>")
    bad = unknown_numbers(draft, report) if draft else ["no draft"]
    return governance.fill_record(report, context=None if bad else draft.removeprefix("Context: ")), bad


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parent))
    import fake_server_l400
    server, url = fake_server_l400.start_in_thread()
    stream = [c["ticket"] for c in governance.eval_gate.load_cases()] * 10
    report = governance.evaluate_candidate(url, "fake-model", "fake-model:v2", stream)
    record, bad = assisted_record(report, lambda p: ask(p, url, "fake-model"))
    print("unknown numbers:", bad)
    print(record.split("## Evidence")[0].strip())
    tampered = lambda p: "Context: candidate fake-model:v2 passed 20/20 golden cases (100%) with 0 regressions."
    print("tampered draft unknown numbers:", assisted_record(report, tampered)[1])
