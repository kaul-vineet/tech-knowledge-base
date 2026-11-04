"""Library equivalent (pending-ci): our series/integral Bessel functions and disk curve against SciPy.

pip install -r ../requirements.txt   (scipy 1.18.1)        python bessel_scipy.py
"""
import numpy as np
from scipy.special import i0, i1, k0, k1

import galaxy as g


def max_relative_error():
    y = np.linspace(0.05, 6.0, 200)
    ours = np.array([g.bessel_i(0, y), g.bessel_i(1, y), g.bessel_k(0, y), g.bessel_k(1, y)])
    ref = np.array([i0(y), i1(y), k0(y), k1(y)])
    return float(np.max(np.abs(ours / ref - 1)))


if __name__ == "__main__":
    print(f"max relative error of I0, I1, K0, K1 on 0.05..6: {max_relative_error():.2e}")
