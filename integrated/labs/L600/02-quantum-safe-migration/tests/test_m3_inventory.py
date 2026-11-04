import json
import unittest

import _lab
import inventory

EXPECTED = json.loads((_lab.LAB / "EXPECTED_INVENTORY.json").read_text(encoding="utf-8"))


class TestM3Inventory(unittest.TestCase):
    def test_recall_and_precision(self):
        s = inventory.score(inventory.scan("before"), EXPECTED["before"])
        self.assertEqual((s["recall"], s["precision"]), (1.0, 1.0), s)

    def test_words_are_not_uses(self):
        files = {(f["file"], f["line"]) for f in inventory.scan("before")}
        self.assertNotIn(("sample_repo/config/edge/nginx.conf", 2), files)          # commented-out planned config
        self.assertFalse(any(f["algorithm"].startswith("RSA") and "reports" in f["file"] for f in inventory.scan("before")))

    def test_after_stage_messaging_goes_through_registry(self):
        msg = [f for f in inventory.scan("after") if f["service"] == "messaging"]
        self.assertTrue(msg and all("(via registry)" in f["algorithm"] for f in msg))


if __name__ == "__main__":
    unittest.main()
