"""Agent assist (optional): a LOCAL model proposes tonight's observing list and explains the sky table.

Safety boundary: deterministic code decides. The agent only PROPOSES which stars are visible and EXPLAINS
the table; code computes every altitude (sky.py), decides what is up, and checks every number the agent quotes.
Only star names and the computed table are sent to the model - never keys, tokens or private data.

python agent_assist.py --fake    # deterministic fake model server (no download, used by the tests)
python agent_assist.py           # local Ollama / llama.cpp server at LOCAL_MODEL_URL (default http://localhost:11434/v1)
"""
import argparse
import json
import re
import sys
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared" / "local_agent"))  # vendored helper
from client import chat  # noqa: E402

import sky  # noqa: E402

MARKER = "[[ASTRO-SKY]]"  # lets the fake server recognise this lab's prompts; harmless for a real model
WHEN = datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)  # 21:00 IST
SYSTEM = "You help plan and explain sky observations. You never run code and never make decisions."
PLAN_PROMPT = (f"{MARKER} Observer in Gurgaon, India (28.46 N, 77.03 E) at 21:00 IST on 2026-10-29. From this list "
               f"{sorted(sky.STARS)} which stars are above the horizon? Reply with ONE JSON object: "
               '{"visible": [names], "reason": "..."}.')
EXPLAIN_PROMPT = (f"{MARKER} Explain this sky table in 2 sentences for a beginner. Quote only numbers that "
                  "appear in the table.\n<results>\n{table}\n</results>")


def extract_object(reply):
    match = re.search(r"\{.*\}", reply, re.S)  # models often wrap the object in prose or ``` fences
    if not match:
        raise ValueError("no {...} object in the reply")
    return json.loads(match.group(0))


def validate(proposal):
    """Only known star names pass; anything else is reported, never computed."""
    names = proposal.get("visible") if isinstance(proposal, dict) else None
    if not isinstance(names, list):
        raise ValueError("'visible' must be a list of star names")
    known = [n for n in names if isinstance(n, str) and n in sky.STARS]
    unknown = [n for n in names if n not in known]
    return known, unknown


def decide(rows, proposed):
    up = {name for name, _, _, is_up in rows if is_up}  # the decision: computed altitude > 0
    return sorted(up), sorted(set(proposed) - up), sorted(up - set(proposed))


def check_numbers(text, rows):
    known = [v for _, alt, az, _ in rows for v in (round(alt, 2), round(az, 2))]
    ok, unverified = [], []
    for token in re.findall(r"-?\d+(?:\.\d+)?", text):
        decimals = len(token.split(".")[1]) if "." in token else 0
        tol = 0.5 * 10 ** -decimals + 1e-9
        (ok if any(abs(float(token) - k) <= tol for k in known) else unverified).append(token)
    return ok, unverified


def assist(base_url=None, model=None):
    ask = lambda prompt: chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                              base_url=base_url, model=model)
    proposal = extract_object(ask(PLAN_PROMPT))
    known, unknown = validate(proposal)
    rows = sky.sky_table(*sky.GURGAON, WHEN)  # code computes the sky, not the agent
    up, wrong, missed = decide(rows, known)
    table = "\n".join(["star | alt | az | up"] + [f"{n} | {a:.2f} | {z:.2f} | {'yes' if u else 'no'}" for n, a, z, u in rows])
    explanation = ask(EXPLAIN_PROMPT.replace("{table}", table))
    ok, unverified = check_numbers(explanation, rows)
    return {"proposal": proposal, "unknown": unknown, "up": up, "wrong": wrong, "missed": missed,
            "table": table, "explanation": explanation, "verified": ok, "unverified": unverified}


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
        sys.exit(f"Code rejected the agent's reply: {exc}")
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("1. agent proposed:", json.dumps(r["proposal"]))
    print(f"2. code decided (altitude > 0): up = {r['up']}")
    print(f"   overruled (agent said visible, code says below): {r['wrong'] or 'none'}; missed: {r['missed'] or 'none'}; unknown names: {r['unknown'] or 'none'}")
    print("3. agent explained:", r["explanation"])
    print(f"4. code checked {len(r['verified']) + len(r['unverified'])} quoted numbers: {len(r['verified'])} match the table; "
          f"UNVERIFIED (treat as the model's guess): {', '.join(r['unverified']) or 'none'}")


if __name__ == "__main__":
    main()
