import importlib.util
import unittest

import numpy as np

import nbody as nb


class TestPhysics(unittest.TestCase):
    def test_two_body_acceleration_matches_newton(self):
        pos = np.array([[0.0, 0, 0], [1.0, 0, 0]])
        a = nb.accelerations(pos, np.array([1.0, 0.0]))
        self.assertAlmostEqual(a[1, 0], -nb.G, places=12)  # GM/r^2 towards the Sun
        self.assertEqual(a[0, 0], 0.0)

    def test_newtons_third_law(self):
        pos, _ = nb.initial_state()
        a = nb.accelerations(pos, nb.MASSES)
        self.assertLess(np.abs(nb.MASSES @ a).max(), 1e-15)  # forces cancel in pairs

    def test_circular_speed(self):
        _, vel = nb.initial_state()
        self.assertAlmostEqual(np.linalg.norm(vel[1]), 2 * np.pi, places=12)


class TestIntegrators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.euler = nb.run(nb.step_euler, years=2.0, dt=0.001)
        cls.leap = nb.run(nb.step_leapfrog, years=2.0, dt=0.001)

    def test_leapfrog_conserves_energy_far_better(self):
        self.assertLess(self.leap[2], 1e-9)
        self.assertGreater(self.euler[2], 1000 * self.leap[2])

    def test_leapfrog_keeps_earth_at_1_au(self):
        pos = self.leap[0]
        self.assertAlmostEqual(np.linalg.norm(pos[1] - pos[0]), 1.0, delta=0.01)

    def test_leapfrog_is_time_reversible(self):
        pos, vel = nb.initial_state()
        p, v = pos, vel
        for _ in range(500):
            p, v = nb.step_leapfrog(p, v, nb.MASSES, 0.002)
        for _ in range(500):
            p, v = nb.step_leapfrog(p, v, nb.MASSES, -0.002)
        self.assertLess(np.abs(p - pos).max(), 1e-9)


@unittest.skipUnless(importlib.util.find_spec("rebound"), "rebound not installed (runs in CI)")
class TestReboundEquivalent(unittest.TestCase):
    def test_rebound_agrees_on_earth_distance(self):
        import nbody_rebound
        ours, theirs = nbody_rebound.compare()
        self.assertAlmostEqual(ours, theirs, delta=1e-4)


if __name__ == "__main__":
    unittest.main()
