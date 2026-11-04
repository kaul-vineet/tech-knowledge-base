"""Agent assist (lesson 15): a LOCAL model drafts the incident summary from SLO burn data; code checks every number.

Safety boundary: code computes the facts and decides the alert; the agent only words them. Every number in the
draft must be one of the facts, and a labelled number (p99, p95, mean, burn rate) must be THAT fact. Nothing is posted.
Run:  python agent_assist.py          (deterministic fake model, no download)
      python agent_assist.py --real   (Ollama/llama.cpp at LOCAL_MODEL_URL, default http://localhost:11434/v1)
"""
import argparse
import re
import sys
from datetime import datetime, timezone

from failure_lab import HERE, load
from traffic import END, lines

sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent (vendored helper)
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

SYSTEM = "You draft incident summaries for an on-call engineer to review. Use only the facts given."
NUMBER = re.compile(r"\d+(?:\.\d+)?")
LABELLED = {"p99": "p99_ms", "p95": "p95_ms", "mean": "mean_ms", "burn rate": "burn_rate"}


def facts(now=END.timestamp()):
    """Computed by code from the request log (solution/slo.py); the model never computes a number."""
    slo = load(HERE / "solution" / "slo.py", "slo_solution")
    records = slo.parse(lines())
    page = next(a for a in slo.alerts(records, now) if a["sli"] == "latency")
    report = slo.latency_report(records, now)
    first_slow = next(r for r in slo.window(records, now, 6 * 3600) if not slo.SLIS["latency"][1](r)
                      and slo.SLIS["latency"][0](r))
    hhmm = lambda t: datetime.fromtimestamp(t, timezone.utc).strftime("%H:%M UTC")  # noqa: E731
    return {"evaluated_at": hhmm(now), "alert": f"{page['sli']} {page['severity']}", "windows": page["windows"],
            "burn_rate": str(page["burn_long"]), "slow_since": hhmm(first_slow["t"]),
            "p99_ms": str(report["p99"]), "p95_ms": str(report["p95"]), "mean_ms": str(report["mean"]),
            "budget_used_1h": f"{page['burn_long'] / 720:.1%}",  # burn rate x 1 h / 720 h (30 days)
            "availability_3d": f"{1 - slo.bad_ratio(slo.window(records, now, 3 * 86400), 'availability'):.4%}"}


def build_prompt(fact_lines, problems=()):
    text = ["[[INCIDENT-SUMMARY]] Draft a 3-4 sentence incident summary for the on-call channel.",
            "Use only the numbers in the brief, each with its label; do not guess causes."]
    if problems:  # check -> retry: the checker's findings go back to the agent
        text.append("Problems: " + "; ".join(problems) + ". Rewrite the summary.")
    return "\n".join(text) + "\n<brief>\n" + "\n".join(f"{k}: {v}" for k, v in fact_lines.items()) + "\n</brief>"


def check_summary(text, fact_lines):
    """Deterministic judge: every number must come from the facts; labelled numbers must match their own fact."""
    allowed = {n for value in fact_lines.values() for n in NUMBER.findall(value)} | {"30"}  # 30-day SLO period
    values = re.sub(r"\bp(50|95|99)\b", "", text)  # p99 is a label, not a value
    problems = [f"number {n} is not in the facts" for n in NUMBER.findall(values) if n not in allowed]
    for label, key in LABELLED.items():
        for found in re.findall(rf"{label}\D{{0,25}}?({NUMBER.pattern})", text, re.I):
            if found != fact_lines[key]:
                problems.append(f"{label} is {fact_lines[key]}, the draft says {found}")
    problems += [f"missing {key} {fact_lines[key]}" for key in ("p99_ms", "burn_rate") if fact_lines[key] not in text]
    return problems


def draft(base_url, model, fact_lines, attempts=2):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": build_prompt(fact_lines)}]
    log, reply, problems = [], "", ["no attempt"]
    for attempt in range(1, attempts + 1):
        reply = chat(messages, base_url=base_url, model=model)
        problems = check_summary(reply, fact_lines)
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
        print("draft rejected: write the summary by hand from the facts")
        return 1
    print("accepted draft (a human posts it):\n  " + reply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
