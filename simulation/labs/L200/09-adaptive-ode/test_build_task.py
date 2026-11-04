"""buildTask check (lesson 9): event detection. Point the import at your own file to test your version."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
import adaptive_ode as ode  # noqa: E402
import ode_events as SOLUTION  # noqa: E402


class TestEvents(unittest.TestCase):
    def test_coffee_reaches_60_at_exact_time(self):
        t, y = SOLUTION.solve_until(ode.coffee, 0, [90.0], 60, lambda t, y: y[0] - 60.0)
        self.assertAlmostEqual(t, np.log(70 / 40) / 0.05, places=6)
        self.assertAlmostEqual(y[0], 60.0, places=6)

    def test_no_event_returns_none(self):
        t, _ = SOLUTION.solve_until(ode.coffee, 0, [90.0], 5, lambda t, y: y[0] - 60.0)
        self.assertIsNone(t)

    def test_first_fox_peak_found_by_event_on_derivative(self):
        # foxes peak where d(foxes)/dt crosses 0 from above
        ev = lambda t, z: ode.lotka_volterra(t, z)[1]
        t, z = SOLUTION.solve_until(ode.lotka_volterra, 0, [10.0, 5.0], 15, ev)
        self.assertAlmostEqual(z[0], 3.0, places=4)  # at a fox peak rabbits = c / d = 3


if __name__ == "__main__":
    unittest.main()
