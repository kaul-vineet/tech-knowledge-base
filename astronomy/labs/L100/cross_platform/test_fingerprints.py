import json
import platform
import unittest

import fingerprints


class TestSameResultsOnEveryOS(unittest.TestCase):
    def test_outputs_match_golden(self):
        golden = json.loads(fingerprints.GOLDEN.read_text(encoding="utf-8"))
        actual = json.loads(json.dumps(fingerprints.compute()))  # same JSON types as the golden file
        for key, expected in golden.items():
            with self.subTest(key=key, machine=f"{platform.system()} {platform.machine()}"):
                self.assertEqual(actual[key], expected)


if __name__ == "__main__":
    unittest.main()
