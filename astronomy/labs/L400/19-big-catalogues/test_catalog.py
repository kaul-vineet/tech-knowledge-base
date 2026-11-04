"""Unit tests + fault reproduction for lesson 19 (numpy only; pyvo and healpy tests are skipped locally)."""
import importlib.util
import re
import unittest
from pathlib import Path

import numpy as np

import catalog

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("catalog_fixed", HERE / "solution" / "catalog.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)


class TestPieces(unittest.TestCase):
    def test_uniform_on_the_sphere(self):
        cat = catalog.make_catalogue(200_000)
        north = np.mean(cat["dec"] > 30.0)  # area fraction above +30 = (1 - sin 30) / 2 = 0.25
        self.assertAlmostEqual(float(north), 0.25, delta=0.005)

    def test_ra_window_widens_with_declination_and_wraps(self):
        z = fixed.Zones(catalog.make_catalogue(1000))
        (lo, hi), = z.ra_windows(100.0, 60.0, 1.0)
        self.assertAlmostEqual((hi - lo) / 2, 2.0, delta=0.01)  # about 1 / cos 60
        self.assertEqual(len(z.ra_windows(0.2, 10.0, 0.5)), 2)
        self.assertEqual(z.ra_windows(10.0, 89.5, 1.0), [(0.0, 360.0)])

    def test_adql_shape(self):
        q = catalog.adql_cone(83.82, -5.39, 0.05)
        self.assertRegex(q, r"^SELECT .+ FROM gaiadr3\.gaia_source WHERE 1 = CONTAINS\(POINT\('ICRS', ra, dec\), "
                            r"CIRCLE\('ICRS', 83\.82, -5\.39, 0\.05\)\)$")
        self.assertIsNone(re.search(r"REQUEST=doQuery", q))


class TestFailureLab(unittest.TestCase):
    """Shipped ra_windows(): RA +/- radius - no 1/cos(dec) widening, no pole case, no wrap at 0/360."""

    def test_zones_miss_sources_away_from_the_equator_and_at_ra_zero(self):
        rows = catalog.main(n=200_000)
        self.assertEqual([r["wrong_cones"] for r in rows], [0, 247, 247])


class TestEquivalents(unittest.TestCase):
    def test_healpix_agrees_with_brute_force(self):
        try:
            import healpix_check
        except ImportError:
            self.skipTest("healpy not installed (pending-ci; no Windows wheels)")
        self.assertEqual(healpix_check.wrong_cones(), 0)

    def test_pyvo_gaia_cone(self):
        try:
            import pyvo_query
        except ImportError:
            self.skipTest("pyvo not installed (pending-ci; needs network)")
        self.assertGreater(len(pyvo_query.gaia_cone()), 0)


if __name__ == "__main__":
    unittest.main()
