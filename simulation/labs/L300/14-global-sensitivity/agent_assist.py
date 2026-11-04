"""Agent assist (optional): a LOCAL model ranks the inputs from the sensitivity table; code checks the ranking.

Safety boundary: deterministic code decides. The agent sees only the sensitivity table (no model code, no keys).
Code validates the reply (a permutation of the known inputs), ranks by Sobol total-order index ST itself,
reports every position where the agent disagrees, and checks every number the agent quotes against the table.

python agent_assist.py --fake    # deterministic fake model server (used by the tests)
python agent_assist.py           # local Ollama / llama.cpp server at LOCAL_MODEL_URL (default http://localhost:11434/v1)
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared" / "local_agent"))  # vendored helper
from client import chat  # noqa: E402

import sensitivity as sa  # noqa: E402

MARKER = "[[SIM-RANK]]"  # lets the fake server recognise this lab's prompts; harmless for a real model
SYSTEM = "You help interpret sensitivity analyses of simulation models. You never run code and never decide."
RANK = (f"{MARKER} Sensitivity table for daily cooling energy (columns: input | oat_swing | morris_mu_star | "
        "morris_sigma | S1 | ST):\n{table}\nRank ALL inputs from most to least important for the output variance. "
        'Reply with ONE JSON object only: {"ranking": [<input names>], "reason": "<one sentence>"}.')
EXPLAIN = (f"{MARKER} Explain in 2 sentences which inputs matter and why. Quote only numbers in the table.\n"
           "<results>\n{table}\n</results>")
COLS = ("oat_swing", "morris_mu_star", "morris_sigma", "S1", "ST")


def render(rows):
    return "\n".join(f"{r['input']} | " + " | ".join(str(r[c]) for c in COLS) for r in rows)


def validate_ranking(reply):
    match = re.search(r"\{.*\}", reply, re.S)  # models often wrap the object in prose or ``` fences
    obj = json.loads(match.group(0)) if match else None
    ranking = obj.get("ranking") if isinstance(obj, dict) else None
    if not isinstance(ranking, list) or sorted(map(str, ranking)) != sorted(sa.NAMES):
        raise ValueError(f"ranking must list each of {sa.NAMES} exactly once, got {ranking!r}")
    return obj


def check_ranking(agent, rows):
    """The decision: rank by ST (computed by code). Report every position where the agent's ranking differs."""
    decided = sa.ranking(rows, "ST")
    wrong = [f"#{k + 1}: agent {a}, code {c}" for k, (a, c) in enumerate(zip(agent, decided)) if a != c]
    return decided, wrong


def check_numbers(text, rows):
    known = [float(r[c]) for r in rows for c in COLS]
    ok, unverified = [], []
    for token in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text):
        tol = 0.5 * 10 ** -(len(token.split(".")[1]) if "." in token else 0) + 1e-9
        (ok if any(abs(float(token) - k) <= tol for k in known) else unverified).append(token)
    return ok, unverified


def assist(base_url=None, model=None):
    rows = sa.table()
    ask = lambda prompt: chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                              base_url=base_url, model=model)
    proposal = validate_ranking(ask(RANK.replace("{table}", render(rows))))
    decided, wrong = check_ranking(proposal["ranking"], rows)
    explanation = ask(EXPLAIN.replace("{table}", render(rows)))
    ok, unverified = check_numbers(explanation, rows)
    return {"rows": rows, "proposal": proposal, "decided": decided, "wrong": wrong, "explanation": explanation,
            "verified": ok, "unverified": unverified}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fake", action="store_true", help="use the deterministic fake model server")
    base_url, server = None, None
    if parser.parse_args().fake:
        import fake_model_server
        server, base_url = fake_model_server.start_in_thread()  # binds 127.0.0.1 on a free port
    try:
        r = assist(base_url)
    except (urllib.error.URLError, ConnectionError) as exc:
        sys.exit(f"No model server reachable ({exc}). Start Ollama, or run: python agent_assist.py --fake")
    except ValueError as exc:
        sys.exit(f"Code rejected the agent's ranking: {exc}")
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("1. code computed the table (input | oat_swing | mu* | sigma | S1 | ST):")
    print("\n".join("   " + line for line in render(r["rows"]).splitlines()))
    print("2. agent ranked:", " > ".join(r["proposal"]["ranking"]), f"({r['proposal'].get('reason', '')})")
    print("3. code ranks by ST:", " > ".join(r["decided"]))
    print(f"4. code verdict: {'agrees' if not r['wrong'] else 'OVERRULED at ' + '; '.join(r['wrong'])}")
    print("5. agent explained:", r["explanation"])
    print(f"6. code checked {len(r['verified']) + len(r['unverified'])} quoted numbers: {len(r['verified'])} match; "
          f"UNVERIFIED (treat as the model's guess): {', '.join(r['unverified']) or 'none'}")


if __name__ == "__main__":
    main()
