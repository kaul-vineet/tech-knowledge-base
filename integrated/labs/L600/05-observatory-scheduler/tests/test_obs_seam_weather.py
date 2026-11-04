"""SEAM simulation <-> scheduler: the promise (analytic p_complete) must match what the weather simulation delivers."""
import math
import unittest

import numpy as np

from tests import _lab

import weather  # noqa: E402


class WeatherPromises(unittest.TestCase):
    def test_chain_reproduces_its_stationary_clear_fraction(self):
        clear = weather.clear_matrix(2000, 64, 11)
        p = weather.pi_clear()
        self.assertLess(abs(clear.mean() - p), 4 * math.sqrt(p * (1 - p) / clear.size) * 8)  # x8: slots correlate

    def test_each_promised_block_completes_as_often_as_promised(self):
        r = _lab.night()
        clear = weather.clear_matrix(1000, len(r["slots"]), 7)
        for s, n, i in r["local"]:
            p = weather.p_complete(n)
            z = abs(clear[:, s:s + n].all(1).mean() - p) / math.sqrt(p * (1 - p) / 1000)
            with self.subTest(target=r["reqs"][i].name):
                self.assertLessEqual(z, 3.0)

    def test_persistence_makes_long_blocks_riskier_than_independent_slots(self):
        self.assertGreater(weather.p_complete(18), weather.pi_clear() ** 18)

    def test_common_random_numbers_and_stream_stability(self):
        a, b = weather.clear_matrix(100, 64, 7), weather.clear_matrix(1000, 64, 7)
        self.assertTrue(np.array_equal(a, b[:100]))  # adding runs never changes old runs (SeedSequence.spawn)


if __name__ == "__main__":
    unittest.main()
