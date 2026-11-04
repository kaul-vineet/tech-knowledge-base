"""What the release is built from (lesson 21). Rows are SYNTHETIC stand-ins, but the licences and credit lines are
the real ones, quoted from the providers' pages (retrieved 2026-10-29), so the licence rules can be practised.

- Gaia DR3 astrometry: "Gaia data are distributed under the CC BY-NC 3.0 IGO license." (cosmos.esa.int/web/gaia-users/license)
- TESS light curves via MAST: most MAST data are public domain; MAST asks for the mission acknowledgement.
- Our own photometry and periods: we choose the licence (CC-BY-4.0).
"""
import numpy as np

INPUTS = [
    {"name": "gaia_dr3_astrometry", "licence": "LicenseRef-CC-BY-NC-3.0-IGO", "family": "BY-NC",
     "credit": ("This work has made use of data from the European Space Agency (ESA) mission Gaia "
                "(https://www.cosmos.esa.int/gaia), processed by the Gaia Data Processing and Analysis Consortium "
                "(DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium). Funding for the DPAC has been provided "
                "by national institutions, in particular the institutions participating in the Gaia Multilateral "
                "Agreement.")},
    {"name": "tess_light_curves", "licence": "LicenseRef-Public-Domain-MAST", "family": "PD",
     "credit": ("This paper includes data collected with the TESS mission, obtained from the MAST data archive at the "
                "Space Telescope Science Institute (STScI). Funding for US Institutions for the TESS mission is provided "
                "by the NASA Explorer Program.")},  # first two sentences of MAST's text; the page continues
    {"name": "own_photometry", "licence": "CC-BY-4.0", "family": "BY",
     "credit": "Photometry and periods: Astro KB lab 21 (synthetic)."},
]


def rows(n=8, seed=21):
    rng = np.random.default_rng(seed)
    return [{"source_id": int(4_000_000 + i), "ra": round(float(rng.uniform(80, 90)), 6),
             "dec": round(float(rng.uniform(-10, 0)), 6), "parallax": round(float(rng.uniform(0.5, 5.0)), 4),
             "tmag": round(float(rng.uniform(8, 13)), 3), "period_d": round(float(rng.uniform(0.3, 12.0)), 5)}
            for i in range(n)]
