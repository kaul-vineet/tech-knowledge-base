"""Agent assist (lab 15): a LOCAL model reads a convergence log, diagnoses it and proposes optimizer settings;
code checks every claim and runs the proposal before accepting it.

Run:  python agent_assist.py --fake    # deterministic fake model server, no download (output in README)
      python agent_assist.py           # your local model (Ollama): LOCAL_MODEL_URL, LOCAL_MODEL env vars
Safety boundary: the model only PROPOSES. Code recomputes the numbers from the log, applies its own diagnosis
rule, checks ranges and the shot budget, then runs the proposal (seeded) and measures the error itself.
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

import numpy as np

import solution_spsa as sol
import vqe_lab as lab

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "_shared"))   # vendored helper: labs/_shared/local_agent
from local_agent.client import chat  # noqa: E402

MARKER = "[[VQE-LOG]]"   # routing tag for the fake server; a real model ignores it
SYSTEM = ("You review convergence logs of variational quantum optimizers. Reply with one fenced code block holding "
          '{"diagnosis": "converged" | "shot_noise" | "learning_rate_too_high" | "not_converged", '
          '"best_energy": number taken from the log, "proposal": {"optimizer": "gd" | "spsa", "shots": int, ...settings}}.')
BUDGET = 2_000_000       # total shots one optimizer run may use
TARGET = 0.03            # accepted error vs the exact ground energy
QUESTIONS = {"diagnose": "Diagnose this run and propose new optimizer settings.",
             "report": "Report the best energy reached and suggest a fix.",
             "costly": "Propose the most reliable settings regardless of cost."}
FENCE = re.compile(r"```(?:\w+)?[ \t]*\n(.*?)```", re.S)
RANGES = {"a": (0, 5), "c": (0.01, 1), "lr": (0, 2), "h": (1e-4, 0.5), "shots": (100, 10_000_000)}


def code_diagnosis(summary):
    """Deterministic rule the model's diagnosis is compared with."""
    if summary["tail_energy_std"] < 0.01:
        return "converged"
    if (summary["tail_grad_norm_median"] or 0) > 5 and summary["tail_energy_std"] > 0.05:
        return "shot_noise"      # gradient norm ~ noise / h: the estimator, not the landscape, drives the steps
    return "not_converged"


def parse(reply):
    m = FENCE.search(reply)
    try:
        return json.loads(m.group(1) if m else reply[reply.find("{"):reply.rfind("}") + 1])
    except ValueError:
        return None


def run_proposal(p):
    settings = {k: v for k, v in p.items() if k not in ("optimizer", "shots")}
    if p["optimizer"] == "spsa":
        return sol.vqe(p["shots"], seed=0, **settings)[1]
    return lab.vqe(p["shots"], seed=0, **settings)[1]


def check(reply, summary):
    data = parse(reply)
    if not isinstance(data, dict) or not isinstance(data.get("proposal"), dict):
        return "REJECT", ["no valid proposal"]
    notes, ok = [], True
    if abs(float(data.get("best_energy", np.inf)) - summary["best_energy_est"]) > 1e-3:
        ok = False
        notes.append(f"best_energy {data.get('best_energy')} is not in the log (log min {summary['best_energy_est']})")
    if data.get("diagnosis") != code_diagnosis(summary):
        ok = False
        notes.append(f"diagnosis {data.get('diagnosis')!r} != code rule {code_diagnosis(summary)!r}")
    p = data["proposal"]
    bad = [k for k, (lo, hi) in RANGES.items() if k in p and not lo < float(p[k]) <= hi]
    if p.get("optimizer") not in ("gd", "spsa") or bad or set(p) - set(RANGES) - {"optimizer"}:
        return "REJECT", notes + [f"proposal outside allowed settings: {p}"]
    cost = 2 * p["shots"] * (3 * sol.SETTINGS["iters"] if p["optimizer"] == "spsa" else 9 * 100)
    if cost > BUDGET:
        return "REJECT", notes + [f"proposal needs {cost:,} shots > budget {BUDGET:,} (not run)"]
    err = run_proposal(p)                                   # code runs it; the model never does
    notes.append(f"code ran {p['optimizer']} @ {p['shots']} shots: error {err}")
    return ("ACCEPT" if ok and err < TARGET else "REJECT"), notes


def run(base_url=None, show=False):
    path = HERE / "logs" / "vqe_gd_1000.jsonl"
    lab.vqe(1000, log_path=path)                               # the failing run from the lab
    summary = lab.summarize(path)
    tail = path.read_text(encoding="utf-8").splitlines()[-5:]
    results = {}
    for name, question in QUESTIONS.items():
        user = f"{MARKER} {question}\nSummary: {json.dumps(summary)}\nLast rows:\n" + "\n".join(tail)
        reply = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], base_url=base_url)
        if show:
            print(f"--- model reply for {name} ---\n{reply}\n")
        results[name] = check(reply, summary)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fake", action="store_true", help="use the deterministic fake model server")
    parser.add_argument("--show", action="store_true", help="print each raw model reply")
    args = parser.parse_args(argv)
    server, base_url = None, None
    if args.fake:
        import fake_vqe_rule
        from local_agent import fake_model_server
        fake_vqe_rule.register(fake_model_server)
        server, base_url = fake_model_server.start_in_thread()   # binds 127.0.0.1 only
    try:
        results = run(base_url, args.show)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"No local model reachable ({e}). Start Ollama or run with --fake.")
    finally:
        if server:
            server.shutdown()
    for name, (verdict, notes) in results.items():
        print(f"{name:8s} {verdict}  " + "; ".join(notes))


if __name__ == "__main__":
    main()
