"""Build-task solution for lab 12: a noise-aware Bell/GHZ check that passes a correct circuit on a noisy
device but still fails a broken one. Run: python solution_tolerant_check.py

Two statistical checks instead of "no other outcome may appear":
  1. success = P(all 0) + P(all 1) must not be far BELOW what the noise model predicts (catches a missing CX);
  2. the all-1 share among those successes must match the model (catches a missing H: all '00', success 1.0).
'Far' = more than Z standard errors of a binomial with the observed number of shots.
"""
import math

import noise_lab as lab

Z = 4.0   # ~6e-5 one-sided false-alarm rate per check; widen if you run thousands of checks a day


def bell_check(counts, n=2, shots=None, noise=None):
    noise = lab.NOISE if noise is None else noise
    shots = shots or sum(counts.values())
    model = lab.metrics(n, noise)
    zeros, ones = counts.get("0" * n, 0), counts.get("1" * n, 0)
    s = model["success"]
    if (zeros + ones) / shots < s - Z * math.sqrt(s * (1 - s) / shots):
        return False                                          # too many 'impossible' outcomes for this noise
    share = model["p_all1"] / (model["p_all0"] + model["p_all1"])
    hits = max(zeros + ones, 1)
    return abs(ones / hits - share) <= Z * math.sqrt(share * (1 - share) / hits)


if __name__ == "__main__":
    noisy = lab.counts(2, lab.NOISE)
    print("noisy Bell counts:", noisy, "-> tolerant check:", bell_check(noisy))
    print("ideal Bell counts -> tolerant check:", bell_check(lab.counts(2, lab.IDEAL), noise=lab.IDEAL))
    passed = sum(bell_check(lab.counts(3, lab.NOISE, seed=s), n=3) for s in range(200))
    print(f"GHZ-3, 200 seeds on the noisy model: {passed}/200 pass")
