import math
import unittest

import falling as f


class TestFalling(unittest.TestCase):
    def test_euler_error_is_first_order(self):
        exact = f.H0 - 0.5 * f.G * 9
        e1 = abs(f.run(f.step_euler, 0.1, 3.0, False)[0] - exact)
        e2 = abs(f.run(f.step_euler, 0.01, 3.0, False)[0] - exact)
        self.assertAlmostEqual(e1 / e2, 10, delta=0.5)

    def test_rk4_exact_without_drag(self):
        y, v = f.run(f.step_rk4, 0.1, 3.0, False)
        self.assertAlmostEqual(y, f.H0 - 0.5 * f.G * 9, places=9)
        self.assertAlmostEqual(v, -f.G * 3, places=9)

    def test_drag_matches_closed_form_tanh(self):
        # independent cross-check: falling from rest with quadratic drag, |v(t)| = Vt * tanh(g t / Vt)
        vt = f.terminal_velocity()
        _, v = f.run(f.step_rk4, 0.001, 2.0, True)
        self.assertAlmostEqual(abs(v), vt * math.tanh(f.G * 2.0 / vt), places=6)

    def test_never_exceeds_terminal_velocity(self):
        _, v = f.time_to_ground(f.step_rk4, 0.001, True)
        self.assertLess(abs(v), f.terminal_velocity())

    def test_no_drag_fall_time(self):
        t, _ = f.time_to_ground(f.step_rk4, 0.001, False)
        self.assertAlmostEqual(t, math.sqrt(2 * f.H0 / f.G), delta=0.002)


try:
    import falling_scipy
except ImportError:  # SciPy runs in CI only
    falling_scipy = None


@unittest.skipIf(falling_scipy is None, "scipy not installed (pending-ci)")
class TestSciPyEquivalent(unittest.TestCase):
    def test_solve_ivp_agrees_with_rk4(self):
        t_ivp, _ = falling_scipy.fall(True)
        t_rk4, _ = f.time_to_ground(f.step_rk4, 0.001, True)
        self.assertAlmostEqual(t_ivp, t_rk4, delta=0.002)


if __name__ == "__main__":
    unittest.main()
