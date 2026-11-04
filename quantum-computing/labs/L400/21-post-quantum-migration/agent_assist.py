"""Agent assist (lab 21): a LOCAL model drafts migration notes from the inventory; code checks every fact.

Run:  python agent_assist.py --fake    # deterministic fake model server (output in README)
      python agent_assist.py           # your local model (Ollama): LOCAL_MODEL_URL, LOCAL_MODEL
Only file paths, line numbers and algorithm names are sent - never keys, tokens or source code.
Code checks: each cited file:line is in the inventory with that algorithm, the replacement and priority match
the code's plan, every P1 item is covered, symmetric crypto is not 'replaced', and any year is 2030 or 2035.
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

import pqc_lab as lab
import solution_scanner as scanner

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from local_agent.client import chat  # noqa: E402

MARKER = "[[PQC-NOTES]]"
SYSTEM = ("You write post-quantum migration notes. One line per quantum-vulnerable item, exactly: "
          "'- <file>:<line> | <algorithm> | <replacement> | <P1|P2>'. Use only items from the inventory.")
QUESTIONS = {"draft": "Draft the migration notes.", "summarise": "Summarise the migration in a few lines.",
             "creative": "Creative mode: add anything else you think matters."}
LINE = re.compile(r"^- (\S+):(\d+) \| (.+?) \| (.+?) \| (P\d)\s*$", re.M)
SHORT = {"key-establishment": "ML-KEM-768", "signature": "ML-DSA-65"}


def check(reply, steps):
    by_loc = {(s["file"], s["line"]): s for s in steps}
    notes, cited = [], set()
    for file, line, algo, repl, prio in LINE.findall(reply):
        s = by_loc.get((file, int(line)))
        if s is None:
            notes.append(f"{file}:{line} is not in the inventory")
            continue
        cited.add((file, int(line)))
        if algo != s["algorithm"]:
            notes.append(f"{file}:{line} algorithm {algo!r} != {s['algorithm']!r}")
        if s["usage"] == "symmetric":
            notes.append(f"{file}:{line} is symmetric ({s['algorithm']}): keep it, do not replace")
        elif repl != SHORT[s["usage"]]:
            notes.append(f"{file}:{line} replacement {repl!r} != {SHORT[s['usage']]!r}")
        if s["usage"] != "symmetric" and prio != s["priority"][:2]:
            notes.append(f"{file}:{line} priority {prio} != {s['priority'][:2]}")
    missing = [f"{f}:{n}" for (f, n), s in by_loc.items() if s["priority"].startswith("P1") and (f, n) not in cited]
    notes += [f"P1 item missing: {m}" for m in missing]
    prose = LINE.sub("", reply)                                             # years in prose, not in 'RSA-2048'
    notes += [f"year {y} is not a NIST IR 8547 date" for y in re.findall(r"\b(20\d\d)\b", prose) if y not in ("2030", "2035")]
    return ("ACCEPT" if not notes else "REJECT"), notes


def run(base_url=None, show=False):
    steps = lab.plan(scanner.scan())
    facts = [{k: s[k] for k in ("file", "line", "algorithm", "usage", "secrecy_years")} for s in steps]   # no secrets
    results = {}
    for name, question in QUESTIONS.items():
        user = f"{MARKER} {question}\nInventory: {json.dumps(facts)}"
        reply = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], base_url=base_url)
        if show:
            print(f"--- model reply for {name} ---\n{reply}\n")
        results[name] = check(reply, steps)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fake", action="store_true", help="use the deterministic fake model server")
    parser.add_argument("--show", action="store_true", help="print each raw model reply")
    args = parser.parse_args(argv)
    server, base_url = None, None
    if args.fake:
        import fake_pqc_rule
        from local_agent import fake_model_server
        fake_pqc_rule.register(fake_model_server)
        server, base_url = fake_model_server.start_in_thread()      # binds 127.0.0.1 only
    try:
        results = run(base_url, args.show)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"No local model reachable ({e}). Start Ollama or run with --fake.")
    finally:
        if server:
            server.shutdown()
    for name, (verdict, notes) in results.items():
        print(f"{name:9s} {verdict}  " + "; ".join(notes))


if __name__ == "__main__":
    main()
