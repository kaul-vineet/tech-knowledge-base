"""Agent assist (optional): a LOCAL model proposes a sensitivity sweep and explains the results.

Safety boundary: deterministic code decides. The agent only PROPOSES a sweep plan and EXPLAINS a results
table; code validates the plan, runs the simulation (vv.py) and checks every number the agent quotes.
Only parameter names and the results table are sent to the model - never keys, tokens or private data.

python agent_assist.py --fake    # deterministic fake model server (no download, used by the tests)
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

import vv  # noqa: E402

MARKER = "[[SIM-SWEEP]]"  # lets the fake server recognise this lab's prompts; harmless for a real model
LAM_RANGE = (0.05, 0.95)  # lam >= mu = 1.0 never reaches steady state, so the formula and the CI are meaningless
CUSTOMER_RANGE = (10_000, 100_000)  # > 5,000 warm-up customers, small enough to run in seconds
MAX_VALUES = 6
SYSTEM = "You help plan and explain simulation experiments. You never run code and never make decisions."
PLAN_PROMPT = (f"{MARKER} A single-server queue model has service rate mu = 1.0 per minute. Propose a sensitivity "
               'sweep over the arrival rate. Reply with ONE JSON object only: {"parameter": "lam", '
               '"values": [up to 6 arrival rates], "customers": integer customers per replication}.')
EXPLAIN_PROMPT = (f"{MARKER} Explain this results table in 2-3 sentences for an engineer. Quote only numbers "
                  "that appear in the table.\n<results>\n{table}\n</results>")


def extract_object(reply):
    match = re.search(r"\{.*\}", reply, re.S)  # models often wrap the object in prose or ``` fences
    if not match:
        raise ValueError("no {...} object in the reply")
    return json.loads(match.group(0))


def validate_plan(plan):
    """Code decides what runs. Returns (accepted lam values, customers, list of rejected/ignored items)."""
    if not isinstance(plan, dict) or plan.get("parameter") != "lam":
        raise ValueError("plan must be an object with parameter 'lam' (the only sweepable input)")
    values, customers = plan.get("values"), plan.get("customers", 20_000)
    if not isinstance(values, list) or not values:
        raise ValueError("'values' must be a non-empty list")
    if type(customers) is not int or not CUSTOMER_RANGE[0] <= customers <= CUSTOMER_RANGE[1]:
        raise ValueError(f"'customers' must be an integer in {CUSTOMER_RANGE}")
    accepted, problems = [], [f"ignored key {k!r}" for k in plan if k not in ("parameter", "values", "customers")]
    for v in values:
        if type(v) not in (int, float):  # type check, not isinstance: True/False are ints in Python
            problems.append(f"{v!r}: not a number")
        elif not LAM_RANGE[0] <= v <= LAM_RANGE[1]:  # also rejects NaN (every comparison is False)
            problems.append(f"{v}: outside [{LAM_RANGE[0]}, {LAM_RANGE[1]}] (unstable or trivial queue)")
        elif float(v) in accepted:
            problems.append(f"{v}: duplicate")
        else:
            accepted.append(float(v))
    if len(accepted) > MAX_VALUES:
        problems.append(f"kept the first {MAX_VALUES} values")
        accepted = accepted[:MAX_VALUES]
    if not accepted:
        raise ValueError("no valid values left: " + "; ".join(problems))
    return sorted(accepted), customers, problems


def run_sweep(values, customers):
    rows = []
    for lam in values:
        mean, half = vv.replicate(lam, reps=10, n=customers)  # the simulation itself: code, not the agent
        rows.append((f"{lam:.2f}", f"{mean:.3f}", f"{half:.3f}", f"{vv.formula(lam):.3f}"))
    return rows


def format_table(rows):
    lines = ["lam | simulated mean wait (min) | 95% CI half-width | M/M/1 formula (min)"]
    return "\n".join(lines + [" | ".join(r) for r in rows])


def check_numbers(text, rows, customers):
    """Every number the agent quotes must match the table (to its shown decimals) or a known input."""
    known = [float(x) for r in rows for x in r] + [vv.MU, 10, 95, customers]
    ok, unverified = [], []
    for token in re.findall(r"\d+(?:\.\d+)?", text):
        decimals = len(token.split(".")[1]) if "." in token else 0
        tol = 0.5 * 10 ** -decimals + 1e-9  # "4.05" may quote 4.046; "19.0" must be within 0.05 of a real value
        (ok if any(abs(float(token) - k) <= tol for k in known) else unverified).append(token)
    return ok, unverified


def assist(base_url=None, model=None):
    ask = lambda prompt: chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                              base_url=base_url, model=model)
    proposal = ask(PLAN_PROMPT)
    values, customers, problems = validate_plan(extract_object(proposal))
    rows = run_sweep(values, customers)
    table = format_table(rows)
    explanation = ask(EXPLAIN_PROMPT.replace("{table}", table))
    ok, unverified = check_numbers(explanation, rows, customers)
    return {"proposal": extract_object(proposal), "values": values, "customers": customers, "problems": problems,
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
    except ValueError as exc:  # includes unparseable replies: the agent's plan never reaches the simulator
        sys.exit(f"Code rejected the agent's plan: {exc}")
    finally:
        if server:
            server.shutdown()
            server.server_close()  # release the port (no ResourceWarning)
    print("1. agent proposed:", json.dumps(r["proposal"]))
    print(f"2. code validated: run lam={r['values']} with {r['customers']} customers; rejected: {'; '.join(r['problems']) or 'none'}")
    print("3. code ran 10 replications per value:")
    print("\n".join("   " + line for line in r["table"].splitlines()))
    print("4. agent explained:", r["explanation"])
    print(f"5. code checked {len(r['verified']) + len(r['unverified'])} quoted numbers: "
          f"{len(r['verified'])} match the table; UNVERIFIED (treat as the model's guess): {', '.join(r['unverified']) or 'none'}")


if __name__ == "__main__":
    main()
