"""Solution: replications from a target half-width (sequential procedure; Law & Kelton style, Welch CI)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import stats  # noqa: E402

N0 = 10  # pilot: below 10 runs the variance estimate (and the t quantile) is too unstable to plan with


def required_replications(requested, a, b, half_width):
    n = len(a)
    if n < N0:
        return max(requested, N0)
    _, hw, _ = stats.welch_ci(a, b)
    return max(requested, n, math.ceil(n * (hw / half_width) ** 2))  # half-width shrinks like 1/sqrt(n)
