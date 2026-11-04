"""Try-it checks for lab 13. Run: python try_it.py   (numpy only)"""
import numpy as np

import mitigation_lab as lab
import solution_constrained as sol


def zne_shot_noise(shots=2000, seeds=200):
    """Try 1: estimate P(000) from 2000 shots per scale. What happens to the spread of the ZNE estimate?"""
    raw, rich = [], []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        v = [lab.noisy_value(s, shots=shots, rng=rng) for s in (1, 3, 5)]
        raw.append(v[0])
        rich.append(lab.richardson([1, 3, 5], v))
    return {"raw_mean": round(float(np.mean(raw)), 4), "raw_std": round(float(np.std(raw)), 4),
            "richardson_mean": round(float(np.mean(rich)), 4), "richardson_std": round(float(np.std(rich)), 4)}


def clip_vs_constrained(seeds=200):
    """Try 2: instead of constrained least squares, clip negatives to 0 and renormalise. Mean TVD over seeds?"""
    def clip(p_noisy, m_est):
        q = np.clip(lab.mitigate(p_noisy, m_est), 0, None)
        return q / q.sum()
    return {"clip": sol.mean_tvd(clip, 100, 200, seeds), "constrained": sol.mean_tvd(sol.mitigate, 100, 200, seeds)}


if __name__ == "__main__":
    print("zne_shot_noise      ", zne_shot_noise())
    print("clip_vs_constrained ", clip_vs_constrained())
