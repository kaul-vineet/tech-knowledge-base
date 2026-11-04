"""Build-task solution for lab 15: replace the finite-difference optimizer with SPSA so shot noise cannot
blow up the gradient. Run: python solution_spsa.py

SPSA (Spall): perturb ALL parameters at once by +-c_k, two evaluations per step whatever the dimension;
gains a_k = a / (A + k + 1)^alpha, c_k = c / (k + 1)^gamma with Spall's alpha = 0.602, gamma = 0.101.
c_k stays ~0.1-0.2, so the noise in (f+ - f-) is divided by 2 c_k, not by a tiny h.
"""
import json
from pathlib import Path

import numpy as np

import vqe_lab as lab

SETTINGS = {"a": 1.0, "c": 0.2, "A": 10, "alpha": 0.602, "gamma": 0.101, "iters": 150}


def spsa(f, x, rng, a, c, A, alpha, gamma, iters, log=None):
    for k in range(iters):
        ak, ck = a / (A + k + 1) ** alpha, c / (k + 1) ** gamma
        delta = rng.choice([-1.0, 1.0], len(x))
        g = (f(x + ck * delta) - f(x - ck * delta)) / (2 * ck) * delta
        x = x - ak * g
        if log:
            log({"iter": k, "energy_est": round(f(x), 5), "step": round(float(ak * np.linalg.norm(g)), 4),
                 "evals": 3 * (k + 1)})
    return x


def vqe(shots=1000, seed=0, log_path=None, **overrides):
    s = {**SETTINGS, **overrides}
    rng = np.random.default_rng(seed)
    f = (lambda t: lab.energy(t)) if shots is None else (lambda t: lab.energy(t, shots, rng))
    lines = []
    x = spsa(f, np.full(4, 0.1), rng, log=lines.append, **s)
    if log_path:
        Path(log_path).parent.mkdir(exist_ok=True)
        Path(log_path).write_text("".join(json.dumps({"optimizer": "spsa", "shots": shots, **ln}) + "\n" for ln in lines),
                                  encoding="utf-8")
    return x, round(lab.energy(x) - lab.E0, 4)


if __name__ == "__main__":
    path = lab.HERE / "logs" / "vqe_spsa_1000.jsonl"
    x, err = vqe(1000, log_path=path)
    print(json.dumps({"optimizer": "spsa", "shots": 1000, "error": err, "log": path.name, **lab.summarize(path)}))
    print("errors over seeds 0-5:", [vqe(1000, seed=s)[1] for s in range(6)])
