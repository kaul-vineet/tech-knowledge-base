import unittest
from functools import partial

import numpy as np

import adaptive_ode as ode


class TestDormandPrince(unittest.TestCase):
    def test_tableau_is_consistent(self):
        self.assertAlmostEqual(sum(ode.B), 1.0)  # weights sum to 1
        self.assertAlmostEqual(sum(ode.E), 0.0)  # 5th and 4th order weights both sum to 1 -> difference sums to 0
        for c, a in zip(ode.C, ode.A):
            self.assertAlmostEqual(sum(a), c)  # row sums equal the stage times

    def test_single_step_is_fifth_order(self):
        # y' = y, y(0) = 1: one step of h has error ~ h^6; halving h cuts it by ~64
        f = lambda t, y: y
        e1 = abs(ode.dp_step(f, 0, np.array([1.0]), 0.2)[0][0] - np.exp(0.2))
        e2 = abs(ode.dp_step(f, 0, np.array([1.0]), 0.1)[0][0] - np.exp(0.1))
        self.assertGreater(e1 / e2, 40)

    def test_tighter_tolerance_means_smaller_error_and_more_steps(self):
        exact = 20 + 70 * np.exp(-0.05 * 30)
        runs = [ode.solve(ode.coffee, 0, [90.0], 30, rtol=r, atol=1e-12) for r in (1e-3, 1e-6, 1e-9)]
        errors = [abs(ys[-1, 0] - exact) for _, ys, _ in runs]
        steps = [len(ts) for ts, _, _ in runs]
        self.assertEqual(errors, sorted(errors, reverse=True))
        self.assertEqual(steps, sorted(steps))
        self.assertLess(errors[-1], 1e-7)

    def test_ends_exactly_at_t_end(self):
        ts, _, _ = ode.solve(ode.coffee, 0, [90.0], 30)
        self.assertEqual(ts[-1], 30)

    def test_lotka_volterra_conserves_invariant(self):
        ts, ys, _ = ode.solve(ode.lotka_volterra, 0, [10.0, 5.0], 15, rtol=1e-9)
        v = lambda z: z[0] - 3 * np.log(z[0]) + z[1] - 1.5 * np.log(z[1])
        self.assertLess(abs(v(ys[-1]) - v(ys[0])), 1e-6)

    def test_stiff_problem_needs_many_explicit_steps_at_any_tolerance(self):
        loose = len(ode.solve(ode.rc_filter, 0, [0.0], 10, rtol=1e-3, atol=1e-9)[0])
        self.assertGreater(loose, 2_000)  # stability limit h ~ 3 tau, not accuracy, sets the step
        stiffer = len(ode.solve(partial(ode.rc_filter, tau=2e-3), 0, [0.0], 10, rtol=1e-3, atol=1e-9)[0])
        self.assertAlmostEqual(loose / stiffer, 2.0, delta=0.2)  # steps scale with 1 / tau


try:
    import ode_scipy
except ImportError:  # SciPy runs in CI only
    ode_scipy = None


@unittest.skipIf(ode_scipy is None, "scipy not installed (pending-ci)")
class TestSciPyEquivalent(unittest.TestCase):
    def test_event_time_matches_exact(self):
        self.assertAlmostEqual(ode_scipy.coffee_event(), np.log(70 / 40) / 0.05, places=5)

    def test_implicit_solver_needs_far_fewer_evaluations_on_stiff_rc(self):
        self.assertLess(ode_scipy.rc_work("Radau")[0] * 5, ode_scipy.rc_work("RK45")[0])


if __name__ == "__main__":
    unittest.main()
