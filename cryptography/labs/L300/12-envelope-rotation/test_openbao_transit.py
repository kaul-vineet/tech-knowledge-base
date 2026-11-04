"""Offline parser test always runs; the live test needs an OpenBao dev server with transit enabled (CI, ubuntu)."""
import os
import unittest
import uuid

import openbao_transit as ob


class TestOffline(unittest.TestCase):
    def test_key_version(self):
        self.assertEqual(ob.key_version("vault:v1:XjsPWPjqPrBi1N2Ms2s1QM798YyFWnO4TR4lsFA="), 1)
        with self.assertRaises(ValueError):
            ob.key_version("orders-kek:v1:abc")


@unittest.skipUnless(os.environ.get("BAO_ADDR") and os.environ.get("BAO_TOKEN"), "no OpenBao dev server (BAO_ADDR/BAO_TOKEN)")
class TestLive(unittest.TestCase):
    def test_rotate_rewrap_retire(self):
        self.assertEqual(ob.demo(key="kl12-" + uuid.uuid4().hex[:8]), (1, 2))


if __name__ == "__main__":
    unittest.main()
