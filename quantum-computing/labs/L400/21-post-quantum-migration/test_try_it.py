"""Tests for lab 21 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryIt(unittest.TestCase):
    def test_longer_secrecy_promotes_the_api_client(self):
        self.assertEqual(try_it.longer_secrecy(), ["toy_app/api_client.py:11", "toy_app/billing.py:7", "toy_app/sync.py:7"])

    def test_upgrade_receivers_before_senders(self):
        self.assertEqual(try_it.old_receiver(), "receiver rejects envelope: unknown kem 'x25519+ml-kem-768'")


if __name__ == "__main__":
    unittest.main()
