"""Agent assist (capstone): a LOCAL model explains the release scorecard; code checks the explanation.

The verdict is computed by run_capstone.py. The note is rejected if its verdict word differs, if it quotes other
counts, or if a NO-GO note does not name every failed criterion. Nothing is sent; a human posts the note.
Run:  python agent_assist.py --fault cross-tenant-policy   (fake model; shows a rejected optimistic GO)
      python agent_assist.py --real                        (Ollama/llama.cpp at LOCAL_MODEL_URL)
"""
import argparse
import io
import json
import pathlib
import re
import sys

import run_capstone
import scorecard

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent (vendored helper)
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

SYSTEM = "You explain release scorecards to a review meeting. Use only the facts given; never change the verdict."


def facts(fault=None):
    buffer = io.StringIO()
    run_capstone.main(["--fault", fault] if fault else [], out=buffer)
    summary = json.loads(buffer.getvalue().splitlines()[-1])
    return {"passed": str(summary["passed"]), "total": str(summary["total"]),
            "failed": ", ".join(summary["failed"]) or "none", "verdict": summary["verdict"]}


def build_prompt(f, problems=()):
    text = ["[[GO-NO-GO]] Write a two-sentence release note from the scorecard summary in the brief."]
    if problems:
        text.append("Problems: " + "; ".join(problems) + ". Rewrite the note.")
    return "\n".join(text) + "\n<brief>\n" + "\n".join(f"{k}: {v}" for k, v in f.items()) + "\n</brief>"


def check_note(text, f):
    problems = []
    said = "NO-GO" if re.search(r"\bNO-GO\b", text) else "GO" if re.search(r"(?<!NO-)\bGO\b", text) else None
    if said != f["verdict"]:
        problems.append(f"verdict is {f['verdict']}, the note says {said}")
    numbers = set(re.findall(r"\d+", re.sub(r"\b(M\d|N\+1)\b", "", text)))
    problems += [f"number {n} is not in the scorecard" for n in sorted(numbers - {f["passed"], f["total"]})]
    if f["verdict"] == "NO-GO":
        problems += [f"failed criterion not named: {c}" for c in f["failed"].split(", ") if c not in text]
    return problems


def draft(base_url, model, f, attempts=2):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": build_prompt(f)}]
    log, reply, problems = [], "", ["no attempt"]
    for attempt in range(1, attempts + 1):
        reply = chat(messages, base_url=base_url, model=model)
        problems = check_note(reply, f)
        log.append(f"attempt {attempt}: " + ("OK" if not problems else "REJECTED") + "".join(f"\n  - {p}" for p in problems))
        if not problems:
            break
        messages += [{"role": "assistant", "content": reply}, {"role": "user", "content": build_prompt(f, problems)}]
    return reply, problems, log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--fault", choices=scorecard.FAULTS)
    args = parser.parse_args(argv)
    f, server = facts(args.fault), None
    if args.real:
        base_url, model = None, None
    else:
        server, base_url = fake_model_server.start_in_thread()
        model = "fake-model"
    try:
        print("scorecard (computed by code): " + ", ".join(f"{k}={v}" for k, v in f.items()))
        reply, problems, log = draft(base_url, model, f)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("\n".join(log))
    print("note rejected: write it by hand" if problems else "accepted note (a human posts it):\n  " + reply)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
