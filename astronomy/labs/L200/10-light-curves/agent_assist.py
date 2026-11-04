"""Agent assist (optional): a LOCAL model proposes a class and period for a light curve and explains the result.

Safety boundary: deterministic code decides. The agent sees only summary numbers, PROPOSES a class + period and
EXPLAINS the result table; code computes the periodogram, decides the period and class, names a 1-day alias,
and flags every number in the explanation that is not in the table. No keys, tokens or private data are sent.

python agent_assist.py --fake    # deterministic fake model server (used by the tests)
python agent_assist.py           # local Ollama / llama.cpp server at LOCAL_MODEL_URL
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared" / "local_agent"))  # vendored helper
from client import chat  # noqa: E402

import periods  # noqa: E402

MARKER = "[[ASTRO-PERIOD]]"
CLASSES = ("pulsating variable", "transit", "unknown")
SYSTEM = "You help classify and explain light curves. You never run code and never make decisions."
PLAN_PROMPT = (f"{MARKER} A star was observed on 23 nights from one site. Summary: {{summary}}. Which class is it, "
               f"one of {list(CLASSES)}, and what is its period in days? Reply with ONE JSON object: "
               '{"class": "...", "period_days": number, "reason": "..."}.')
EXPLAIN_PROMPT = f"{MARKER} Explain this result in 2 sentences. Quote only numbers from the table.\n<results>\n{{table}}\n</results>"


def extract_object(reply):
    m = re.search(r"\{.*\}", reply, re.S)
    if not m:
        raise ValueError("no {...} object in the reply")
    return json.loads(m.group(0))


def validate(p):
    if not isinstance(p, dict) or p.get("class") not in CLASSES:
        raise ValueError(f"class must be one of {CLASSES}")
    if type(p.get("period_days")) not in (int, float) or not 0.05 <= p["period_days"] <= 100:
        raise ValueError("period_days must be a number in [0.05, 100]")
    return p["class"], float(p["period_days"])


def decide(r):
    """Code's rule: strong periodic power -> pulsating variable; weak power but one-sided dips -> transit."""
    if r["power"] > 0.3:
        return "pulsating variable"
    return "transit" if r["skew"] > 0.5 else "unknown"


def judge_period(agent_p, code_p):
    if abs(agent_p - code_p) / code_p < 0.01:
        return "agrees"
    if abs(abs(1 / agent_p - 1 / code_p) - 1) < 0.01:  # frequencies differ by 1 cycle/day: sampling alias
        return "overruled: 1-day alias of the code's period"
    return "overruled"


def check_numbers(text, rows):
    known = [float(v) for v in rows.values()]
    ok, bad = [], []
    for token in re.findall(r"\d+(?:\.\d+)?", text):
        decimals = len(token.split(".")[1]) if "." in token else 0
        (ok if any(abs(float(token) - k) <= 0.5 * 10**-decimals + 1e-9 for k in known) else bad).append(token)
    return ok, bad


def assist(base_url=None, model=None):
    ask = lambda prompt: chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                              base_url=base_url, model=model)
    t = periods.sample_times()
    y = periods.variable_star(t)
    summary = {"points": int(t.size), "baseline_days": round(float(t.max() - t.min()), 1),
               "amplitude_mag": round(float(y.max() - y.min()), 2), "skew": round(periods.skewness(y), 2)}
    agent_class, agent_p = validate(extract_object(ask(PLAN_PROMPT.replace("{summary}", json.dumps(summary)))))
    r = periods.analyse(t, y)  # the periodogram: code, not the agent
    code_class = decide(r)
    rows = {"best_period_days": f"{r['best_period_days']:.4f}", "power": f"{r['power']:.3f}", "skew": f"{r['skew']:.2f}"}
    table = "\n".join(f"{k} | {v}" for k, v in rows.items())
    explanation = ask(EXPLAIN_PROMPT.replace("{table}", table))
    ok, bad = check_numbers(explanation, rows)
    return {"agent": (agent_class, agent_p), "code": (code_class, rows["best_period_days"]),
            "verdict": judge_period(agent_p, r["best_period_days"]), "class_agrees": agent_class == code_class,
            "explanation": explanation, "verified": ok, "unverified": bad}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fake", action="store_true")
    base_url, server = None, None
    if parser.parse_args().fake:
        import fake_model_server
        server, base_url = fake_model_server.start_in_thread()
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
    print(f"1. agent proposed: class={r['agent'][0]!r}, period={r['agent'][1]} d")
    print(f"2. code decided: class={r['code'][0]!r} (agent {'agrees' if r['class_agrees'] else 'overruled'}), "
          f"period={r['code'][1]} d -> agent period {r['verdict']}")
    print("3. agent explained:", r["explanation"])
    print(f"4. code checked {len(r['verified']) + len(r['unverified'])} quoted numbers: {len(r['verified'])} match; "
          f"UNVERIFIED (treat as the model's guess): {', '.join(r['unverified']) or 'none'}")


if __name__ == "__main__":
    main()
