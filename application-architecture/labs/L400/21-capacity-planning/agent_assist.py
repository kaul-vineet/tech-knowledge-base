"""Agent assist (lesson 21): a LOCAL model drafts the capacity memo; code checks every number in it.

Safety boundary: code computes the plan and decides the instance count; the agent only words the memo.
Every number must be a fact; labelled numbers (peak, capacity, in flight, cost, N instances) must be THAT fact.
Run:  python agent_assist.py          (deterministic fake model, no download)
      python agent_assist.py --real   (Ollama/llama.cpp at LOCAL_MODEL_URL, default http://localhost:11434/v1)
"""
import argparse
import re
import sys

from app import HERE, load, plan

sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent (vendored helper)
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

SYSTEM = "You draft capacity memos for an architecture review. Use only the facts given."
NUMBER = re.compile(r"\d+(?:\.\d+)?")
LABELLED = {"peak of": "peak_rps", "capacity of": "capacity_rps", "gives": "in_flight_at_peak",
            "cost of": "cost_per_million_usd"}


def facts():
    """Computed by code (solution/capacity.py); the model never computes a number."""
    p = plan(load(HERE / "solution" / "capacity.py", "capacity_solution"))
    chosen = next(o for o in p["options"] if o["option"] == "async email")
    rejected = next(o for o in p["options"] if o["option"] == "sync email")
    return {"peak_rps": str(p["model"]["peak_rps"]), "avg_rps": str(p["model"]["avg_rps"]),
            "mean_service_ms": str(p["model"]["mean_service_ms"]), "in_flight_at_peak": str(p["in_flight_at_peak"]),
            "capacity_rps": str(chosen["capacity_rps"]), "instances": str(chosen["instances"]),
            "p99_at_peak_ms": str(chosen["p99_at_peak_ms"]), "p99_one_down_ms": str(chosen["p99_one_down_ms"]),
            "cost_per_million_usd": str(chosen["cost_per_million_usd"]), "email_senders": str(p["email_senders"]),
            "rejected_option": "sync email", "rejected_instances": str(rejected["instances"])}


def build_prompt(fact_lines, problems=()):
    text = ["[[CAPACITY-MEMO]] Draft a short capacity memo for the architecture review.",
            "Use only the numbers in the brief, each with its label; recommend the instance count given."]
    if problems:  # check -> retry: the checker's findings go back to the agent
        text.append("Problems: " + "; ".join(problems) + ". Rewrite the memo.")
    return "\n".join(text) + "\n<brief>\n" + "\n".join(f"{k}: {v}" for k, v in fact_lines.items()) + "\n</brief>"


def check_memo(text, fact_lines):
    """Deterministic judge: every number from the facts; labelled numbers equal their own fact."""
    allowed = {n for value in fact_lines.values() for n in NUMBER.findall(value)} | {"1", "99"}  # N+1, p99
    problems = [f"number {n} is not in the facts" for n in NUMBER.findall(text) if n not in allowed]
    for label, key in LABELLED.items():
        for found in re.findall(rf"{label}\D{{0,30}}?({NUMBER.pattern})", text, re.I):
            if found != fact_lines[key]:
                problems.append(f"{key} is {fact_lines[key]}, the memo says {found}")
    for found in re.findall(r"(\d+) instances", text):
        if found not in (fact_lines["instances"], fact_lines["rejected_instances"]):
            problems.append(f"the plan is {fact_lines['instances']} instances, the memo says {found}")
    problems += [f"missing {k} {fact_lines[k]}" for k in ("peak_rps", "instances", "p99_one_down_ms")
                 if fact_lines[k] not in text]
    return problems


def draft(base_url, model, fact_lines, attempts=2):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": build_prompt(fact_lines)}]
    log, reply, problems = [], "", ["no attempt"]
    for attempt in range(1, attempts + 1):
        reply = chat(messages, base_url=base_url, model=model)
        problems = check_memo(reply, fact_lines)
        log.append(f"attempt {attempt}: " + ("OK" if not problems else "REJECTED") + "".join(f"\n  - {p}" for p in problems))
        if not problems:
            break
        messages += [{"role": "assistant", "content": reply}, {"role": "user", "content": build_prompt(fact_lines, problems)}]
    return reply, problems, log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--real", action="store_true", help="use a real local model instead of the fake server")
    args = parser.parse_args(argv)
    fact_lines, server = facts(), None
    if args.real:
        base_url, model, label = None, None, "local model (LOCAL_MODEL_URL / LOCAL_MODEL)"
    else:
        server, base_url = fake_model_server.start_in_thread()
        model, label = "fake-model", "fake model server (deterministic stand-in, not a language model)"
    try:
        print(f"model: {label}")
        print("facts (computed by code): " + ", ".join(f"{k}={v}" for k, v in fact_lines.items()))
        reply, problems, log = draft(base_url, model, fact_lines)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("\n".join(log))
    if problems:
        print("memo rejected: write it by hand from the facts")
        return 1
    print("accepted memo (a human reviews and signs it):\n  " + reply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
