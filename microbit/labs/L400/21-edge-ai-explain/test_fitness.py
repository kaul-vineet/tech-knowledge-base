"""Fitness function (lab 21): keeps ADR-0021 true.

For 200 seeded adversarial replies x 3 seeds: the alarm record's SHA-256 digest equals the digest of
what decide() produced without any model, and every note that is published passes check_reply again
and claims no state change. Proves "the model cannot change an alarm" by test, not by promise.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import solution  # noqa: E402
import fuzz  # noqa: E402
import incident  # noqa: E402
from alarms import decide, freeze  # noqa: E402


class Fitness(unittest.TestCase):
    def test_model_cannot_change_an_alarm(self):
        snap = incident.snapshot()
        code = decide(snap)
        want = freeze(code)[1]
        for seed in (1, 2, 3):
            for kind, text in fuzz.replies(code, seed=seed):
                out = solution.run(lambda m: text, snap)
                with self.subTest(seed=seed, kind=kind):
                    self.assertEqual(out["digest"], want)
                    if out["accepted"]:
                        reply = '{"explanation": %s, "operator_note": %s}' % tuple(
                            solution.json.dumps(out[k]) for k in ("explanation", "note"))
                        self.assertEqual(solution.check_reply(reply, snap, code)[1], [])
                        self.assertIsNone(solution.STATE_CHANGE.search(out["note"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
