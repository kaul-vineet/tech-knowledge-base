"""M5: the poisoned doc makes the model request send_email; the secure host blocks it, the naive host sends it."""
import unittest

import _lab
import scenarios as sc


class TestEndToEnd(unittest.TestCase):
    def test_secure_blocks_naive_sends(self):
        secure, _ = sc.s2_injection(_lab.url(), _lab.registry())
        naive, _ = sc.s2_injection(_lab.url(), _lab.registry(), {"naive-host"})
        self.assertEqual(secure.world.effects, [])
        blocked = [c for c in secure.host.calls if c["tool"] == "send_email"][0]
        self.assertEqual((blocked["scope_ok"], blocked["allowed"], blocked["executed"]), (False, False, False))
        self.assertEqual(naive.world.effects[0][1]["to"], "attacker@evil.test")


if __name__ == "__main__":
    unittest.main()
