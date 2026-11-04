"""Unit tests + fault reproduction for lesson 18 (numpy + stdlib; the fastavro test is skipped locally)."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

import alert_sim as sim
import alerts
from schema import validate

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("alerts_fixed", HERE / "solution" / "alerts.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)


class TestPieces(unittest.TestCase):
    def test_blur_widens_a_gaussian_in_quadrature(self):
        img = sim.render([(64.0, 64.0, 1.0)], 1.2) - sim.SKY
        out = alerts.blur(img, 1.6)
        sigma = np.sqrt(np.sum(out * (sim.XX - 64) ** 2) / out.sum())
        self.assertAlmostEqual(float(sigma), 2.0, delta=0.01)  # sqrt(1.2^2 + 1.6^2)

    def test_schema_validator_catches_errors(self):
        bad = {"schemavsn": "astro-kb-1.0", "candid": -1, "objectId": "x",
               "candidate": {"mjd": 1.0, "x": 1.0, "y": 1.0, "flux": 1.0, "sigmaflux": 1.0, "isdiffpos": "yes",
                             "rb": 2.0, "fwhm": 1.0}, "prv_candidates": []}
        self.assertEqual(validate(bad), ["$.candid: -1 < 0", "$.candidate.isdiffpos: 'yes' not in ['t', 'f']",
                                         "$.candidate.rb: 2.0 > 1"])

    def test_classifier_rules(self):
        known = [("V1", 10.0, 10.0)]
        star = {"x": 50, "y": 50, "sharp": 1.4, "isdiffpos": "t"}
        self.assertEqual(alerts.classify(dict(star, sharp=8.0), [], known), "bogus")
        self.assertEqual(alerts.classify(dict(star, x=10, y=10), [], known), "known_variable")
        self.assertEqual(alerts.classify(star, [dict(star, x=54)], known), "moving")
        self.assertEqual(alerts.classify(star, [star], known), "transient")


class TestFailureLab(unittest.TestCase):
    """Shipped difference(): new - reference, no PSF or flux matching -> every star leaves a residual."""

    def test_alert_storm(self):
        exposures = sim.nights()
        s = alerts.summary("C", alerts.run("C", exposures), exposures)
        self.assertEqual((s["alerts_per_night"], s["real_fraction"]), (58.2, 0.045))


class TestFixedGolden(unittest.TestCase):
    def test_fixed_options(self):
        exposures = sim.nights()
        got = [fixed.summary(o, fixed.run(o, exposures), exposures) for o in "ABC"]
        self.assertEqual([(g["alerts_per_night"], g["real_fraction"]) for g in got],
                         [(9.8, 0.462), (4.2, 0.882), (3.5, 0.857)])


class TestAvroEquivalent(unittest.TestCase):
    def test_fastavro_round_trip(self):
        try:
            import alert_avro
        except ImportError:
            self.skipTest("fastavro not installed (pending-ci)")
        n, back, _ = alert_avro.round_trip()
        self.assertEqual(n, back)


if __name__ == "__main__":
    unittest.main()
