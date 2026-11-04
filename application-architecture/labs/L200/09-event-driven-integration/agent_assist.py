"""Agent assist (lesson 9): a LOCAL model proposes the AsyncAPI entry for a new event; code decides.

Safety boundary: the agent only proposes text. check_document + validate_event judge it against the real
event that the code would emit; asyncapi.json is never written - a human edits it after review.
Run:  python agent_assist.py          (deterministic fake model, no download)
      python agent_assist.py --real   (Ollama/llama.cpp at LOCAL_MODEL_URL, default http://localhost:11434/v1)
"""
import argparse
import copy
import json
import pathlib
import sys

from asyncapi_check import check_document, load, validate_event
from events import new_event

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent (vendored helper)
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

BRIEF = {"Event": "LoanOverdue", "Channel": "loanOverdue", "Address": "library.loans.overdue",
         "Fields": "eventId:uuid, eventType:string, occurredAt:date-time, loanId:integer, bookId:string, "
                   "memberId:string, daysOverdue:integer"}
# the event the code WILL emit: the proposal must describe this, not the other way round
SAMPLE = new_event("LoanOverdue", {"loanId": 7, "bookId": "b1", "memberId": "m1", "daysOverdue": 3},
                   occurred_at="2026-10-28T08:00:00Z", event_id="0f8e7d6c-5b4a-4392-8170-6f5e4d3c2b1a")
SYSTEM = "You draft API descriptions for review. You only propose; a human accepts or rejects."


def build_prompt(problems=()):
    lines = ["[[EVENT-SCHEMA]] Propose the AsyncAPI 3.1.0 additions for ONE new event of the Library Loans service:",
             "one channel, one operation with action 'send', one message and its payload schema.",
             "Reply with a single object with the keys channels, operations and components only, no prose."]
    if problems:  # check -> retry: the checker's findings go back to the agent, never the other way round
        lines.append("Problems: " + "; ".join(problems) + ". Fix them and return the full object again.")
    return "\n".join(lines) + "\n<brief>\n" + "\n".join(f"{k}: {v}" for k, v in BRIEF.items()) + "\n</brief>"


def validate_proposal(text, base=None):
    """Deterministic judge. Returns (merged document or None, problems)."""
    base = base or load()
    try:
        fragment = json.loads(text.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
    except ValueError:
        return None, ["reply is not a single parseable object"]
    if not isinstance(fragment, dict) or set(fragment) - {"channels", "operations", "components"}:
        return None, ["reply may only contain the keys channels, operations, components"]
    merged, problems = copy.deepcopy(base), []
    for section, items in fragment.items():
        for path, value in _leaves(section, items):
            target = merged
            for key in path[:-1]:
                target = target.setdefault(key, {})
            if path[-1] in target:  # proposals add; they never replace an existing contract
                problems.append(f"{'.'.join(path)} already exists - proposals may only add")
            target[path[-1]] = value
    if BRIEF["Channel"] not in fragment.get("channels", {}):
        return merged, problems + [f"expected a channel named {BRIEF['Channel']}"]
    problems += check_document(merged)
    problems += [f"sample event from code: {p}" for p in validate_event(merged, BRIEF["Channel"], SAMPLE)]
    return merged, problems


def _leaves(section, items):
    if section == "components":
        return [(("components", kind, name), v) for kind, group in items.items() for name, v in group.items()]
    return [((section, name), v) for name, v in items.items()]


def propose(base_url, model, attempts=2):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": build_prompt()}]
    log, merged, problems = [], None, ["no attempt"]
    for attempt in range(1, attempts + 1):
        reply = chat(messages, base_url=base_url, model=model)
        merged, problems = validate_proposal(reply)
        log.append(f"attempt {attempt}: " + ("OK" if not problems else "REJECTED") + "".join(f"\n  - {p}" for p in problems))
        if not problems:
            break
        messages += [{"role": "assistant", "content": reply}, {"role": "user", "content": build_prompt(problems)}]
    return merged, problems, log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--real", action="store_true", help="use a real local model instead of the fake server")
    args = parser.parse_args(argv)
    server = None
    if args.real:
        base_url, model, label = None, None, "local model (LOCAL_MODEL_URL / LOCAL_MODEL)"
    else:
        server, base_url = fake_model_server.start_in_thread()
        model, label = "fake-model", "fake model server (deterministic stand-in, not a language model)"
    try:
        print(f"model: {label}")
        merged, problems, log = propose(base_url, model)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("\n".join(log))
    if problems:
        print("proposal rejected: nothing to review")
        return 1
    channel = merged["channels"][BRIEF["Channel"]]
    print(f"proposal adds: channel {BRIEF['Channel']} ({channel['address']}), operation send{BRIEF['Event']}, "
          f"message {BRIEF['Event']}")
    print("sample LoanOverdue event from code validates against the proposal: OK")
    print(f"asyncapi.json unchanged: {check_document(load()) == [] and 'loanOverdue' not in load()['channels']} "
          "(a human reviews the proposal and edits the file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
