"""Result contract: counts + probabilities WITH uncertainty, raw and readout-mitigated, tied to one calibration.

Raw: p_i = c_i / N, multinomial standard error sqrt(p_i (1 - p_i) / N).
Mitigated: quantum L300 #13 inverse (mitigation_lab.mitigate) with the readout matrix A of the calibration version the
chunks ran on; covariance propagated exactly: Cov_m = A^-1 Cov_raw A^-T, Cov_raw = (diag(p) - p p^T) / N.
"""
import numpy as np

from _kb import dm, mitigation

REQUIRED = ("job_id", "shots", "counts", "probs", "stderr", "mitigated", "mitigated_stderr", "backend",
            "calibration_version")


def build(job_id, counts, n, readout, backend, version, cache_hit=False):
    shots = sum(counts.values())
    p = np.array([counts.get(dm.label(i, n), 0) for i in range(2 ** n)]) / shots
    cov = (np.diag(p) - np.outer(p, p)) / shots
    a_inv = np.linalg.inv(readout)
    m = mitigation.mitigate(p, readout)
    m_err = np.sqrt(np.clip(np.diag(a_inv @ cov @ a_inv.T), 0, None))
    lab = [dm.label(i, n) for i in range(2 ** n)]
    return {"job_id": job_id, "shots": shots, "counts": dict(sorted(counts.items())),
            "probs": {lab[i]: round(float(p[i]), 6) for i in range(2 ** n) if p[i] > 0},
            "stderr": {lab[i]: round(float(np.sqrt(p[i] * (1 - p[i]) / shots)), 6) for i in range(2 ** n) if p[i] > 0},
            "mitigated": {lab[i]: round(float(m[i]), 6) for i in range(2 ** n)},
            "mitigated_stderr": {lab[i]: round(float(m_err[i]), 6) for i in range(2 ** n)},
            "backend": backend, "calibration_version": version, "cache_hit": cache_hit}


def violations(result, requested_shots):
    """The contract a client relies on; an empty list means the result may be returned."""
    out = [f"missing {k}" for k in REQUIRED if k not in result]
    if out:
        return out
    if result["shots"] != requested_shots or sum(result["counts"].values()) != requested_shots:
        out.append(f"shots {sum(result['counts'].values())} != requested {requested_shots}")
    probs, err = result["probs"], result["stderr"]
    if set(err) != set(probs) or any(0 < probs[k] < 1 and err[k] <= 0 for k in probs):
        out.append("every reported probability needs a positive standard error")
    if abs(sum(result["probs"].values()) - 1) > 1e-4:
        out.append("probabilities do not sum to 1")
    return out
