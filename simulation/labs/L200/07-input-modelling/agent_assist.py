"""Agent assist (optional): a LOCAL model proposes which distribution fits the service times and explains the fit table.

Safety boundary: deterministic code decides. The agent sees only summary statistics and the KS table (never the raw
file, keys or private data). Code validates the proposal, fits every candidate, picks the one with the smallest KS D
and checks every number the agent quotes.

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

import fit_inputs as fi  # noqa: E402

MARKER = "[[SIM-FIT]]"  # lets the fake server recognise this lab's prompts; harmless for a real model
ALLOWED = {f(fi.load())["name"] for f in fi.FITTERS}  # the agent may only name a candidate the code can fit
SYSTEM = "You help choose input distributions for simulations. You never run code and never make decisions."
PROPOSE = (f"{MARKER} Service times (minutes) at a repair desk: {{stats}}. Which ONE of {sorted(ALLOWED)} fits best? "
           'Reply with ONE JSON object only: {"distribution": "<name>", "reason": "<one sentence>"}.')
EXPLAIN = (f"{MARKER} Explain this goodness-of-fit table in 2 sentences for an engineer. Smaller D = closer fit. "
           "Quote only numbers that appear in the table.\n<results>\n{table}\n</results>")


def summary(x):
    skew = float(((x - x.mean()) ** 3).mean() / x.std() ** 3)
    return {"n": len(x), "mean": round(float(x.mean()), 2), "sd": round(float(x.std()), 2),
            "cv": round(float(x.std() / x.mean()), 2), "skewness": round(skew, 2),
            "min": float(x.min()), "max": float(x.max())}


def extract_object(reply):
    match = re.search(r"\{.*\}", reply, re.S)  # models often wrap the object in prose or ``` fences
    if not match:
        raise ValueError("no {...} object in the reply")
    return json.loads(match.group(0))


def validate_proposal(obj):
    name = obj.get("distribution") if isinstance(obj, dict) else None
    if not isinstance(name, str) or name.strip().lower() not in ALLOWED:
        raise ValueError(f"distribution must be one of {sorted(ALLOWED)}, got {name!r}")
    return name.strip().lower()


def ks_table(x):
    rows = sorted(((f(x)["name"], fi.ks_statistic(x, f(x)["cdf"])) for f in fi.FITTERS), key=lambda r: r[1])
    return rows, "\n".join(f"{name} | {d:.3f}" for name, d in rows)  # code computes D; the agent only reads it


def check_numbers(text, rows, stats):
    known = [round(d, 3) for _, d in rows] + [float(v) for v in stats.values()]
    ok, unverified = [], []
    for token in re.findall(r"\d+(?:\.\d+)?", text):
        decimals = len(token.split(".")[1]) if "." in token else 0
        tol = 0.5 * 10 ** -decimals + 1e-9  # "0.03" may quote 0.031; "0.05" must be within 0.005 of a real value
        (ok if any(abs(float(token) - k) <= tol for k in known) else unverified).append(token)
    return ok, unverified


def assist(base_url=None, model=None, x=None):
    x = fi.load() if x is None else x
    ask = lambda prompt: chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                              base_url=base_url, model=model)
    stats = summary(x)
    proposal = extract_object(ask(PROPOSE.replace("{stats}", json.dumps(stats))))
    picked = validate_proposal(proposal)
    rows, table = ks_table(x)
    decided = rows[0][0]  # the decision: smallest KS D, computed by code
    rank = [name for name, _ in rows].index(picked) + 1
    explanation = ask(EXPLAIN.replace("{table}", table))
    ok, unverified = check_numbers(explanation, rows, stats)
    return {"stats": stats, "proposal": proposal, "picked": picked, "rank": rank, "rows": rows, "table": table,
            "decided": decided, "explanation": explanation, "verified": ok, "unverified": unverified}


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
    except ValueError as exc:  # unparseable or unknown distribution: nothing is fitted on the agent's word
        sys.exit(f"Code rejected the agent's proposal: {exc}")
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("1. code summarised the data:", json.dumps(r["stats"]))
    print("2. agent proposed:", json.dumps(r["proposal"]))
    print("3. code fitted every candidate (KS D, smallest first):")
    print("\n".join("   " + line for line in r["table"].splitlines()))
    verdict = "agrees" if r["picked"] == r["decided"] else f"is overruled (rank {r['rank']} of {len(r['rows'])})"
    print(f"4. code decided: {r['decided']} - the agent's pick ({r['picked']}) {verdict}; data cv is {r['stats']['cv']}")
    print("5. agent explained:", r["explanation"])
    print(f"6. code checked {len(r['verified']) + len(r['unverified'])} quoted numbers: {len(r['verified'])} match; "
          f"UNVERIFIED (treat as the model's guess): {', '.join(r['unverified']) or 'none'}")


if __name__ == "__main__":
    main()
