"""The two tryIt exercises: expected output = what the lesson prints."""
import sys
import unittest

import _lab

sys.path.insert(0, str(_lab.LAB / "try_it"))
import try_it_1  # noqa: E402
import try_it_2  # noqa: E402


class TestTryIt(unittest.TestCase):
    def test_wider_scope_still_blocked_by_provenance(self):
        self.assertEqual(try_it_1.run(), {"scope_ok": True, "executed": False,
                                          "deny": ["side-effect target not from the user's request"], "effects": []})

    def test_attenuation_cannot_widen(self):
        out = try_it_2.run()
        self.assertEqual(out["send_email"], "caveat not satisfied: tool in search_docs")
        self.assertEqual(len(out["caveats"]), 4)


if __name__ == "__main__":
    unittest.main()
