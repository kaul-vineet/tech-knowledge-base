"""tryIt experiments for lesson 9 (run: python try_it.py)."""
import numpy as np

import photometry as ph

img = ph.make_image()

# 1. Change the aperture radius for the bright star 0 and the faint star 3. Predict: best radius for each?
for r in (2.0, 3.0, 4.0, 6.0, 9.0):
    s0, s3 = ph.measure(img, 30, 30, r=r), ph.measure(img, 30, 72, r=r)
    print(f"r={r:3.1f}: star0 SNR {s0['snr']:6.1f}   star3 SNR {s3['snr']:5.1f}")

# 2. Use the MEAN instead of the median in the annulus, with star 1 moved next to star 0. Predict: who suffers?
ph.STARS[1] = (42.0, 30.0, 8000.0)  # star 1 now sits in star 0's background annulus
img2 = ph.make_image()
m = ph.measure(img2, 30, 30)
yy, xx = np.mgrid[0:101, 0:101]
d2 = (xx - 30) ** 2 + (yy - 30) ** 2
mean_bkg = img2[(d2 >= 100) & (d2 <= 225)].mean()
net_mean = m["net"] + m["npix"] * (m["bkg"] - mean_bkg)  # same aperture sum, mean sky instead of median sky
print(f"median sky {m['bkg']:.2f} -> net {m['net']:.1f} e- | mean sky {mean_bkg:.2f} -> net {net_mean:.1f} e- (true 20000)")
