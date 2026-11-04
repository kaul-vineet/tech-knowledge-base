"""Build-task check: SlidingWindowLog(limit, window, clock) - at most `limit` requests in ANY window.
Default target = solution_ratelimit.py. Test YOUR ratelimit.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

from helpers import SimClock

HERE = Path(__file__).resolve().parent
FILE = "ratelimit.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_ratelimit.py"
spec = importlib.util.spec_from_file_location("target_ratelimit", HERE / FILE)
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)


class TestSlidingWindow(unittest.TestCase):
    def test_no_window_ever_holds_more_than_the_limit(self):
        clock = SimClock()
        lim, accepted = rl.SlidingWindowLog(5, 1.0, clock), []
        for i in range(300):  # a request every 10 ms for 3 s
            clock.t = round(i * 0.01, 2)
            if lim.allow()[0]:
                accepted.append(clock.t)
        for t in accepted:
            self.assertLessEqual(sum(t <= u < t + 1.0 for u in accepted), 5)

    def test_boundary_burst_is_blocked_and_wait_is_exact(self):
        clock = SimClock(0.9)
        lim = rl.SlidingWindowLog(5, 1.0, clock)
        self.assertTrue(all(lim.allow()[0] for _ in range(5)))  # 5 at t=0.9
        clock.t = 1.0  # a fixed 1 s window would reset here and allow 5 more
        ok, wait = lim.allow()
        self.assertEqual((ok, round(wait, 9)), (False, 0.9))  # oldest leaves the window at 1.9
        clock.t = 1.9
        self.assertTrue(lim.allow()[0])

    def test_plugs_into_the_api(self):
        out = rl.run({"alice": (6, True)}, make_limiter=lambda c: rl.SlidingWindowLog(5, 2.5, c))
        self.assertEqual(out["alice"]["trace"], ["200"] * 5 + ["429(wait 3)", "200"])


if __name__ == "__main__":
    unittest.main()
