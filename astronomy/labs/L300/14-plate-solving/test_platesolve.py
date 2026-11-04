"""Unit tests + fault reproduction for lesson 14 (numpy only; the astropy test is skipped locally)."""
import unittest

import numpy as np

import fields
import platesolve
import triangles


class TestProjection(unittest.TestCase):
    def test_tan_round_trip(self):
        ra, dec = np.array([10.0, 10.5, 9.7]), np.array([62.0, 62.3, 61.8])
        back = fields.tan_deproject(*fields.tan_project(ra, dec, 10.2, 62.1), 10.2, 62.1)
        np.testing.assert_allclose(back, (ra, dec), atol=1e-10)

    def test_tangent_point_maps_to_origin_and_scale_is_cos_dec_in_ra(self):
        xi, eta = fields.tan_project(np.array([10.01]), np.array([62.0]), 10.0, 62.0)
        self.assertAlmostEqual(float(xi[0]) / 0.01, np.cos(np.radians(62.0)), places=5)
        self.assertAlmostEqual(float(eta[0]), 0.0, places=6)


class TestTriangles(unittest.TestCase):
    def test_invariants_survive_rotation_scale_and_mirror(self):
        p = np.array([[0.0, 0.0], [3.0, 0.5], [1.0, 2.0]])
        th = np.radians(40)
        R = 2.5 * np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]) @ np.diag([-1, 1])
        a, b = triangles.triangles(p, 3)[0], triangles.triangles(p @ R.T + 7, 3)[0]
        np.testing.assert_allclose(a, b, rtol=1e-12)

    def test_vote_returns_nothing_without_three_catalogue_stars(self):
        self.assertEqual(triangles.vote(np.zeros((5, 2)), np.zeros((2, 2))), {})


class TestFailureLab(unittest.TestCase):
    """Shipped to_plane() uses raw RA/Dec offsets: fine at Dec -5, triangles distorted at Dec +62."""

    def test_orion_solves_cassiopeia_does_not(self):
        self.assertEqual(platesolve.run("orion"), {"field": "orion", "solved": True, "n_matched": 32,
                                                   "rms_arcsec": 0.373, "pointing_error_arcsec": 0.07,
                                                   "scale_arcsec_px": 2.0045, "rotation_deg": 11.991})
        self.assertEqual(platesolve.run("cassiopeia"), {"field": "cassiopeia", "solved": False})


class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_scale_matches(self):
        try:
            import platesolve_astropy
        except ImportError:
            self.skipTest("astropy not installed (pending-ci)")
        for field in fields.FIELDS:
            scale, _ = platesolve_astropy.astropy_wcs(field)
            self.assertAlmostEqual(scale, fields.SCALE_ARCSEC, delta=0.002)


if __name__ == "__main__":
    unittest.main()
