"""Agent assist (lab 05): a LOCAL model drafts OpenQASM from a description; code decides.

Run:  python agent_assist.py --fake    # deterministic fake model server, no download (output in README)
      python agent_assist.py           # your local model (Ollama): LOCAL_MODEL_URL, LOCAL_MODEL env vars
Safety boundary: the model only PROPOSES text. The lab's own parser + numpy statevector
(crosscheck_qasm_numpy.py) accepts or rejects it against a spec written in code.
Model output is never executed as Python and never decides anything.
"""
import argparse
import re
import sys
import urllib.error
from pathlib import Path

import numpy as np

import crosscheck_qasm_numpy as cc   # the judge: the lab's independent OpenQASM reader

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "_shared"))   # vendored helper: labs/_shared/local_agent
from local_agent.client import chat  # noqa: E402

MARKER = "[[QASM-DRAFT]]"   # routing tag for the fake server; a real model ignores it
SYSTEM = ("You write OpenQASM 3 programs. Reply with exactly one program in a ```qasm code block. "
          "Use only h, x and cx from stdgates.inc, then measure every qubit.")
# Spec in code, not in the prompt: the exact outcome probabilities a correct program must give.
TASKS = {
    "bell": ("2 qubits: a Bell pair; both qubits always measure the same value", {"00": 0.5, "11": 0.5}),
    "ghz3": ("3 qubits: a GHZ state; all three qubits always measure the same value", {"000": 0.5, "111": 0.5}),
    "phase": ("2 qubits: a Bell pair with an extra pi/2 phase on qubit 0", {"00": 0.5, "11": 0.5}),
}
FENCE = re.compile(r"```(?:qasm|openqasm\d?)?[ \t]*\n(.*?)```", re.S | re.I)


def draft(description, base_url=None):
    """Ask the model for a program. Returns its raw reply text (untrusted)."""
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"{MARKER} Write an OpenQASM 3 program for: {description}"}]
    return chat(messages, base_url=base_url, temperature=0)


def extract_program(reply):
    m = FENCE.search(reply)
    if m:
        return m.group(1)
    start = reply.find("OPENQASM")
    return reply[start:] if start >= 0 else None


def check(reply, expected):
    """Deterministic verdict on an untrusted reply: (accepted, reason, probabilities)."""
    program = extract_program(reply)
    if program is None:
        return False, "no OpenQASM program found", None
    try:
        probs = cc.probabilities(program)         # unverifiable (outside the parser's subset) = rejected
    except (ValueError, KeyError) as e:
        return False, f"parser: {e}", None
    same = set(probs) == set(expected) and all(abs(probs[k] - expected[k]) < 1e-9 for k in expected)
    reason = "matches spec" if same else f"outcomes {probs} != spec {expected}"
    return same, reason, probs


def sample_counts(probs, shots=1000, seed=7):
    """Seeded shots from the verified probabilities (numpy stand-in for a simulator run)."""
    keys = sorted(probs)
    draws = np.random.default_rng(seed).choice(len(keys), size=shots, p=[probs[k] for k in keys])
    return {k: int(n) for k, n in zip(keys, np.bincount(draws, minlength=len(keys))) if n}


def run(base_url=None, show=False):
    results = {}
    for name, (description, expected) in TASKS.items():
        reply = draft(description, base_url)
        if show:
            print(f"--- model reply for {name} ---\n{reply}\n")
        ok, reason, probs = check(reply, expected)
        results[name] = (ok, reason, sample_counts(probs) if ok else None)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fake", action="store_true", help="use the deterministic fake model server")
    parser.add_argument("--show", action="store_true", help="print each raw model reply")
    args = parser.parse_args(argv)
    server, base_url = None, None
    if args.fake:
        import fake_qasm_rule
        from local_agent import fake_model_server
        fake_qasm_rule.register(fake_model_server)
        server, base_url = fake_model_server.start_in_thread()   # binds 127.0.0.1 only
    try:
        results = run(base_url, args.show)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"No local model reachable ({e}). Start Ollama or run with --fake.")
    finally:
        if server:
            server.shutdown()
    for name, (ok, reason, counts) in results.items():
        verdict = "ACCEPT" if ok else "REJECT"
        extra = f"  counts(1000, seed 7) {counts}" if ok else ""
        print(f"{name:6s} {verdict}  {reason}{extra}")


if __name__ == "__main__":
    main()
