"""failureLab symptom (deterministic host model): the racy take() loses ticks."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import host_sim  # noqa: E402
import race_model  # noqa: E402


class Symptom(unittest.TestCase):
    def test_irq_in_the_window_is_lost(self):
        m = host_sim.schedule(race_model.take, {"window"})
        self.assertEqual((m.isr_total, m.consumed, m.pending, m.lost()), (1, 0, 0, 1))

    def test_only_the_window_is_dangerous(self):
        lost = dict((p, host_sim.schedule(race_model.take, {p}).lost()) for p in ("before", "window", "after"))
        self.assertEqual(lost, {"before": 0, "window": 1, "after": 0})

    def test_soak_loses_about_a_quarter(self):
        m = host_sim.soak(race_model.take)                    # 1000 takes, p_window 0.3, seed 16
        self.assertEqual((m.irqs, m.isr_total, m.consumed, m.pending, m.lost()), (1316, 1316, 1000, 0, 316))


if __name__ == "__main__":
    unittest.main(verbosity=2)
