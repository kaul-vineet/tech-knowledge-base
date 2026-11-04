"""buildTask check: required_replications() must size n from the target half-width.

By default this checks solution/replications.py. To check your edited replications.py instead:
    BUILD_TARGET=mine python -m unittest tests.test_build_task -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file all three tests fail; after your fix they pass.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import pipeline  # noqa: E402
import registry  # noqa: E402

TARGET = "replications.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/replications.py"
rule = pipeline.load_policy(TARGET)


class TestBuildTask(unittest.TestCase):
    def test_pilot_of_at_least_ten(self):
        self.assertGreaterEqual(rule(3, [4.0, 5.0, 3.0], [3.0, 2.0, 2.5], 0.3), 10)

    def test_more_noise_needs_more_replications(self):
        quiet = [4.0, 4.1, 3.9] * 4
        noisy = [2.0, 4.0, 6.0] * 4
        self.assertGreater(rule(3, noisy, noisy, 0.3), rule(3, quiet, quiet, 0.3))

    def test_pipeline_reaches_the_target(self):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(300_000), half_width=0.3, policy=rule)
        res = pl.submit("run_experiment", {"baseline": _fixture.A, "candidate": _fixture.B, "replications": 3, "seed": 13})
        self.assertLessEqual((res["difference"]["ci_high"] - res["difference"]["ci_low"]) / 2, 0.3 + 1e-3)
        self.assertEqual(res["verdict"], "significant decrease")


if __name__ == "__main__":
    unittest.main()
