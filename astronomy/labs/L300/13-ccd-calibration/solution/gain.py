"""Stretch solution (lesson 13): measure gain and read noise from the frames themselves (photon transfer).

gain [e-/ADU] = ((mean F1 + mean F2) - (mean B1 + mean B2)) / (var(F1 - F2) - var(B1 - B2))
read noise [e-] = gain * std(B1 - B2) / sqrt(2)
Differencing two frames cancels the fixed pattern (flat structure, hot pixels); only random noise remains.
Central 32 x 32 box, averaged over 5 frame pairs. python solution/gain.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import camera  # noqa: E402

BOX = (slice(16, 48), slice(16, 48))


def gain_and_read_noise(f):
    """Average over the 5 independent frame pairs (0,1), (2,3), ... - one pair scatters by ~15%."""
    gains, reads = [], []
    for k in range(0, 10, 2):
        b1, b2 = f["bias"][k][BOX], f["bias"][k + 1][BOX]
        f1, f2 = f["flat"][k][BOX], f["flat"][k + 1][BOX]
        g = ((f1.mean() + f2.mean()) - (b1.mean() + b2.mean())) / ((f1 - f2).var() - (b1 - b2).var())
        gains.append(g)
        reads.append(g * (b1 - b2).std() / np.sqrt(2))
    return float(np.mean(gains)), float(np.mean(reads))


if __name__ == "__main__":
    g, rn = gain_and_read_noise(camera.frames())
    print(f"measured gain {g:.3f} e-/ADU (true {camera.GAIN}), read noise {rn:.2f} e- (true {camera.READ_E})")
