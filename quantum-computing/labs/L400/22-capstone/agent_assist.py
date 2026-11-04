"""Capstone agent assist: a LOCAL model explains the benchmark report; code checks the explanation.

Run:  python agent_assist.py --fake    (deterministic fake model server)  |  python agent_assist.py  (Ollama)
The model only EXPLAINS. Code already decided the winner; the check rejects an explanation that names another
winner, quotes a number that is not in the report, or claims a quantum advantage the benchmark cannot show.
Only the report (numbers, solver names) is sent - no keys, no request credentials.
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from local_agent.client import chat  # noqa: E402

MARKER = "[[QOPT-REPORT]]"
SYSTEM = "Explain this optimisation benchmark report to an engineer in 2-4 sentences. Say which solver wins and why."
QUESTIONS = {"explain": "Explain the result.", "pitch": "Pitch the result to management.", "brief": "Brief summary please."}


def numbers(obj):
    if isinstance(obj, dict):
        return set().union(*(numbers(v) for v in obj.values())) if obj else set()
    if isinstance(obj, list):
        return set().union(*(numbers(v) for v in obj)) if obj else set()
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        return {round(float(obj), 4)}
    return set()


def check(text, report):
    notes = []
    named = re.findall(r"\b(greedy|annealing|qaoa-noisy|exact)\b wins", text)
    if not named:
        notes.append("no winner stated")
    elif named[0] != report["winner"]:
        notes.append(f"claims {named[0]} wins; code decided {report['winner']}")
    if re.search(r"quantum advantage|speed-?up", text, re.I):
        notes.append("claims a quantum advantage the benchmark cannot show")
    known = numbers(report) | {round(float(report["request"]["seeds"]), 4)}
    for raw in re.findall(r"(?<![\w.-])(\d+(?:\.\d+)?)%?", text):
        if round(float(raw), 4) not in known:
            notes.append(f"number {raw} is not in the report")
    return ("ACCEPT" if not notes else "REJECT"), notes


def run(report, base_url=None):
    facts = {k: report[k] for k in ("winner", "optimum", "benchmark", "feasibility") if k in report}
    facts.update({k: report[k] for k in ("mitigation", "execution") if k in report})
    results = {}
    for name, question in QUESTIONS.items():
        user = f"{MARKER} {question}\nReport: {json.dumps(facts)}"
        reply = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], base_url=base_url)
        results[name] = (*check(reply, report), reply)
    return results


def main(argv=None):
    import pipeline
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fake", action="store_true")
    args = parser.parse_args(argv)
    server, base_url = None, None
    if args.fake:
        import fake_explain_rule
        from local_agent import fake_model_server
        fake_explain_rule.register(fake_model_server)
        server, base_url = fake_model_server.start_in_thread()
    try:
        results = run(pipeline.solve({}), base_url)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"No local model reachable ({e}). Start Ollama or run with --fake.")
    finally:
        if server:
            server.shutdown()
    for name, (verdict, notes, _) in results.items():
        print(f"{name:8s} {verdict}  " + "; ".join(notes))


if __name__ == "__main__":
    main()
