"""Try-it checks for lab 14. Run: python try_it.py   (numpy only)"""
import numpy as np

import qaoa_lab as lab

P2_BEST = [0.585, 1.029, 0.517, 0.309]      # printed by solution_restarts.py


def random_starts(seeds=8, target=0.92):
    """Try 1: 8 random starts for p = 2 without a warm start. How many reach ratio >= 0.92?"""
    ratios = [lab.ratio(lab.solve(2, seed=s)) for s in range(seeds)]
    return {"ratios": ratios, "hits": int(sum(r >= target for r in ratios))}


def sample_the_answer(shots=20, seed=7):
    """Try 2: sample 20 shots from the p = 2 optimum. Ratio 0.92 is an average; is the best SAMPLE optimal?"""
    probs = np.abs(lab.qaoa_state(P2_BEST)) ** 2
    hits = np.random.default_rng(seed).choice(len(probs), size=shots, p=probs / probs.sum())
    return {"P_optimal": round(float(probs[lab.CUT == 5].sum()), 4), "best_sampled_cut": int(lab.CUT[hits].max()),
            "optimal_samples": int((lab.CUT[hits] == 5).sum())}


if __name__ == "__main__":
    print("random_starts    ", random_starts())
    print("sample_the_answer", sample_the_answer())
