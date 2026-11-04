"""Fitness function for the group-key design (threshold: 0 leaks; commit cost <= 2*log2(n) HPKE encryptions).
A seeded random sequence of removals and key updates in a 16-member group: after every removal nobody removed can
read the new epoch, every current member can, and no commit costs more than the logarithmic budget."""
import math
import random
import unittest

import solution_remove

N = 16


class TestRemovalFitness(unittest.TestCase):
    def test_random_membership_changes(self):
        rng = random.Random(2020)
        names = [f"m{i:02d}" for i in range(N)]
        g = solution_remove.Group(names)
        current, gone = set(names), set()
        for step in range(10):
            committer = rng.choice(sorted(current))
            victim = rng.choice(sorted(current - {committer})) if step % 2 == 0 and len(current) > 2 else None
            cost = g.commit(committer, remove=victim)
            self.assertLessEqual(cost, 2 * math.log2(N), f"step {step}: commit cost {cost}")
            if victim:
                current.discard(victim)
                gone.add(victim)
            msg = g.send(committer, f"step {step}")
            self.assertEqual({n for n in names if g.read(n, msg) is not None}, current, f"step {step}")
        self.assertEqual(len(gone), 5)


if __name__ == "__main__":
    unittest.main()
