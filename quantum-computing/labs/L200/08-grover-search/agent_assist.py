"""Agent assist (lab 08): a LOCAL model proposes the marked states + iteration count; code decides.

Run:  python agent_assist.py --fake    # deterministic fake model server, no download (output in README)
      python agent_assist.py           # your local model (Ollama): LOCAL_MODEL_URL, LOCAL_MODEL env vars
Safety boundary: the model only PROPOSES JSON. The spec is a Python predicate in TASKS; code rebuilds the
marked set from it, compares, and computes the success probability with numpy (crosscheck_numpy.py).
Model output is never executed and never decides anything.
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

import crosscheck_numpy as cc   # the judge: exact Grover probabilities in numpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "_shared"))   # vendored helper: labs/_shared/local_agent
from local_agent.client import chat  # noqa: E402

MARKER = "[[GROVER-ORACLE]]"   # routing tag for the fake server; a real model ignores it
SYSTEM = ('You design Grover searches in Qiskit. Bitstrings are written q(n-1)...q0 (qubit 0 is the RIGHTMOST '
          'character). Reply with one fenced code block holding {"marked": [bitstrings], "iterations": k}.')
MIN_SUCCESS = 0.9
# (Prompts avoid the word "json": the shared fake server routes any request containing it to its own demo rule.)
# Spec in code, not in the prompt: (description, n_qubits, predicate on the integer value of the basis state).
TASKS = {
    "single": ("3 qubits: mark the one state with q0 = 1, q1 = 1, q2 = 0", 3, lambda x: x == 0b011),
    "pair": ("3 qubits: mark every state with exactly two 1s and q2 = 1", 3,
             lambda x: bin(x).count("1") == 2 and x >> 2 & 1),
    "even": ("2 qubits: mark every state whose integer value is even", 2, lambda x: x % 2 == 0),
}
FENCE = re.compile(r"```(?:json)?[ \t]*\n(.*?)```", re.S | re.I)


def propose(description, base_url=None):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"{MARKER} {description}"}]
    return chat(messages, base_url=base_url, temperature=0)


def parse(reply):
    m = FENCE.search(reply)
    text = m.group(1) if m else reply[reply.find("{"):reply.rfind("}") + 1]
    try:
        data = json.loads(text)
        return [str(s) for s in data["marked"]], int(data["iterations"])
    except (ValueError, KeyError, TypeError):
        return None


def check(reply, n, predicate):
    """Deterministic verdict on an untrusted reply: (verdict, reason, iterations_to_use)."""
    proposal = parse(reply)
    if proposal is None:
        return "REJECT", "no valid JSON proposal", None
    marked, k = proposal
    if any(len(s) != n or set(s) - {"0", "1"} for s in marked):
        return "REJECT", f"not {n}-bit strings: {marked}", None
    expected = sorted(format(x, f"0{n}b") for x in range(2 ** n) if predicate(x))   # oracle from the spec
    if sorted(marked) != expected:
        return "REJECT", f"marks {sorted(marked)} but spec needs {expected}", None
    best = cc.optimal_iterations(len(marked), n)
    p_prop, p_best = cc.success(marked, max(k, 0)), cc.success(marked, best)
    if p_best < MIN_SUCCESS:
        return "REJECT", f"oracle ok, but best P(success)={p_best} at k={best}: no amplification (M/N={len(marked)}/{2 ** n})", None
    if p_prop + 1e-9 < p_best:
        return "ACCEPT", f"oracle ok; k={k} gives P={p_prop}, code uses k={best}: P={p_best}", best
    return "ACCEPT", f"oracle ok; k={k} gives P={p_prop}", k


def run(base_url=None, show=False):
    results = {}
    for name, (description, n, predicate) in TASKS.items():
        reply = propose(description, base_url)
        if show:
            print(f"--- model reply for {name} ---\n{reply}\n")
        results[name] = check(reply, n, predicate)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fake", action="store_true", help="use the deterministic fake model server")
    parser.add_argument("--show", action="store_true", help="print each raw model reply")
    args = parser.parse_args(argv)
    server, base_url = None, None
    if args.fake:
        import fake_grover_rule
        from local_agent import fake_model_server
        fake_grover_rule.register(fake_model_server)
        server, base_url = fake_model_server.start_in_thread()   # binds 127.0.0.1 only
    try:
        results = run(base_url, args.show)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"No local model reachable ({e}). Start Ollama or run with --fake.")
    finally:
        if server:
            server.shutdown()
    for name, (verdict, reason, _) in results.items():
        print(f"{name:6s} {verdict}  {reason}")


if __name__ == "__main__":
    main()
