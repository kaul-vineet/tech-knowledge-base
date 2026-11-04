"""M5 (seam: envelope contract versioning): reader contract on the v2 header; v3 (ChaCha20-Poly1305) only after
the replicated gate entry; unknown versions refused; a node-local config makes replicas diverge."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestM5Contract(unittest.TestCase):
    def test_contract_and_gate(self):
        r = sc.m5_contract()
        self.assertEqual(r["v2_contract_problems"], [])
        self.assertEqual(r["renamed_field_problems"], ["missing n"])
        self.assertEqual((r["v3_before_gate"], r["v3_after_gate"], r["v3_aead"]), (409, 201, "C20P1305"))
        self.assertEqual(set(r["readable_per_replica"].values()), {4})
        self.assertTrue(r["unknown_version_9"].startswith("refused"))

    def test_local_config_diverges(self):
        r = sc.m5_contract({"local-contract-config"})
        self.assertGreater(len(set(r["readable_per_replica"].values())), 1)


if __name__ == "__main__":
    unittest.main()
