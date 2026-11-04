"""Lab 15 - a hybrid variational loop (VQE) on a 2-qubit Pauli sum, with shot noise and JSON-lines logs.

Run:  python vqe_lab.py       (numpy only; writes logs/vqe_<optimizer>_<shots>.jsonl next to this file)
SDK path (Qiskit primitives + scipy COBYLA): python vqe_qiskit.py   (runs in CI, not yet observed)
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402

HERE = Path(__file__).resolve().parent
# Toy "H2-like" Hamiltonian (illustrative coefficients, not a chemistry calculation). Labels are Qiskit order:
# "ZI" = Z on qubit 1, I on qubit 0.
TERMS = {"II": -1.05, "ZI": 0.39, "IZ": -0.39, "ZZ": -0.01, "XX": 0.18}
PAULI = {"I": np.eye(2), "Z": np.diag([1.0, -1.0]), "X": np.array([[0.0, 1.0], [1.0, 0.0]])}
H = sum(c * np.kron(PAULI[k[0]], PAULI[k[1]]) for k, c in TERMS.items())
E0 = float(np.linalg.eigvalsh(H)[0])                         # exact ground energy: the referee, not the optimizer
SIGN = 1 - 2 * ((np.arange(4)[:, None] >> np.arange(2)) & 1)  # SIGN[i, q] = eigenvalue of Z_q on basis state i


def ansatz(t):
    return sv.run(2, [(sv.ry(t[0]), 0, ()), (sv.ry(t[1]), 1, ()), sv.cx(0, 1), (sv.ry(t[2]), 0, ()), (sv.ry(t[3]), 1, ())])


def energy(t, shots=None, rng=None):
    """Estimator: exact <H>, or two measured groups (Z basis: II, ZI, IZ, ZZ; X basis: XX) of `shots` each."""
    psi = ansatz(t)
    if shots is None:
        return float(np.real(psi.conj() @ H @ psi))
    pz = np.abs(psi) ** 2
    px = np.abs(sv.run(2, [sv.h(0), sv.h(1)], psi)) ** 2          # rotate to the X basis, then measure
    fz = rng.multinomial(shots, pz / pz.sum()) / shots             # shot noise enters here
    fx = rng.multinomial(shots, px / px.sum()) / shots
    z0, z1 = SIGN[:, 0], SIGN[:, 1]
    return float(TERMS["II"] + TERMS["ZI"] * fz @ z1 + TERMS["IZ"] * fz @ z0
                 + TERMS["ZZ"] * fz @ (z0 * z1) + TERMS["XX"] * fx @ (z0 * z1))


def gradient_descent(f, x, iters=100, lr=0.4, h=1e-3, log=None):
    """Finite-difference gradient: 2 evaluations per parameter per step. Exact on a statevector..."""
    for k in range(iters):
        g = np.array([(f(x + h * e) - f(x - h * e)) / (2 * h) for e in np.eye(len(x))])   # ...noise / h under shots
        x = x - lr * g
        if log:
            log({"iter": k, "energy_est": round(f(x), 5), "grad_norm": round(float(np.linalg.norm(g)), 3),
                 "evals": (2 * len(x) + 1) * (k + 1)})   # +1: the logged estimate
    return x


def vqe(shots=1000, seed=0, log_path=None, iters=100, **gd_settings):
    rng = np.random.default_rng(seed)
    f = (lambda t: energy(t)) if shots is None else (lambda t: energy(t, shots, rng))
    lines = []
    x = gradient_descent(f, np.full(4, 0.1), iters=iters, log=lines.append, **gd_settings)
    if log_path:
        Path(log_path).parent.mkdir(exist_ok=True)
        Path(log_path).write_text("".join(json.dumps({"optimizer": "gd", "shots": shots, **ln}) + "\n" for ln in lines),
                                  encoding="utf-8")
    return x, round(energy(x) - E0, 4)                              # error measured exactly, after the run


def summarize(log_path, tail=20):
    rows = [json.loads(s) for s in Path(log_path).read_text(encoding="utf-8").splitlines()]
    last = rows[-tail:]
    return {"iters": len(rows), "best_energy_est": min(r["energy_est"] for r in rows),
            "final_energy_est": rows[-1]["energy_est"], "evals": rows[-1]["evals"],
            "tail_energy_std": round(float(np.std([r["energy_est"] for r in last])), 4),
            "tail_grad_norm_median": float(np.median([r["grad_norm"] for r in last])) if "grad_norm" in rows[0] else None}


if __name__ == "__main__":
    print(f"exact ground energy E0 = {E0:.4f}")
    for shots in (None, 1000):                                      # happy path, then the fault: shot noise
        path = HERE / "logs" / f"vqe_gd_{shots or 'exact'}.jsonl"
        x, err = vqe(shots, log_path=path)
        print(json.dumps({"optimizer": "gd", "shots": shots, "error": err, "log": path.name, **summarize(path)}))
