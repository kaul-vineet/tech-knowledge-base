"""tryIt experiments for lesson 21 (python try_it.py). Prints what actually happens (times vary by machine)."""
import importlib.util, time
from pathlib import Path

import lincheck
import solution_modelcheck as mc

spec = importlib.util.spec_from_file_location("l300_checker", Path(__file__).resolve().parents[2] / "L300" /
                                              "13-partitions-fault-injection" / "checker.py")
l300 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l300)

# tryIt 1: the L300 exhaustive checker vs the memoised search on growing (non-linearizable) R=1 W=1 histories
quorum = lincheck.load_lab17("quorum")
for run_ms in (10, 30, 50):
    hist = quorum.run(1, 1, 17, run_ms=run_ms)
    t0 = time.perf_counter()
    fast = lincheck.check(hist)[0]
    t1 = time.perf_counter()
    slow = l300.check_register(hist)[0]
    t2 = time.perf_counter()
    print(f"tryIt 1: {len(hist):>3} ops: memoised {fast} in {1000 * (t1 - t0):.2f} ms,"
          f" exhaustive (L300) {slow} in {1000 * (t2 - t1):.1f} ms")

# tryIt 2: state explosion - allow one more term in the (fixed) election model
for max_term in (2, 3):
    mc.MAX_TERM = max_term
    violated, _, states, ms = mc.bfs()
    print(f"tryIt 2: MAX_TERM={max_term}: {states} distinct states, {ms} ms, violation: {violated or 'none'}")
