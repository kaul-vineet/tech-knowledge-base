"""Optional real data (pending-ci, needs network): pi Mensae (TESS sector 1, SPOC) through the same search.

pip install -r ../requirements.txt   (lightkurve 2.6.0)        python fetch_tess.py
Published period of pi Men c: 6.27 d (Huang et al. 2018; Gandolfi et al. 2018). TESS data are public (MAST);
acknowledge TESS and MAST if you publish anything from it (lesson 21).
"""
import lightkurve as lk
import numpy as np

import pipeline


def search_pi_men():
    lc = lk.search_lightcurve("pi Men", mission="TESS", author="SPOC", sector=1).download().remove_nans().normalize()
    t = np.asarray(lc.time.value - lc.time.value[0], float)
    f = np.asarray(lc.flux.value, float)
    keep = np.argsort(t)
    _, cand = pipeline.bls(t[keep], pipeline.detrend(t[keep], f[keep]))
    return cand


if __name__ == "__main__":
    print(search_pi_men())
