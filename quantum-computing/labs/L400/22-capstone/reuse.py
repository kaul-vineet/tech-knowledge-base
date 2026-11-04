"""Import the earlier labs instead of copying them (capstone). Module names are unique across these folders,
so the folders are APPENDED to sys.path (the capstone's own files always win)."""
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]
for folder in ("L400/17-hybrid-architecture", "L400/18-benchmark-vs-classical", "L400/19-resource-estimation",
               "L400/20-error-aware-compilation", "L300/13-error-mitigation", "_shared"):
    if str(LABS / folder) not in sys.path:
        sys.path.append(str(LABS / folder))

import backend as l17_backend  # noqa: E402,F401  lesson 17: adapter interface, FakeClock, simulator
import bench_lab as l18_bench  # noqa: E402,F401  lesson 18: metrics, decide()
import compile_lab as l20_compile  # noqa: E402,F401  lesson 20: routing, cancellation, ESP
import device as l20_device  # noqa: E402,F401  lesson 20: fake ladder device
import estimate_lab as l19_estimate  # noqa: E402,F401  lesson 19: resource estimates
import noisy_check as l20_noisy  # noqa: E402,F401  lesson 20: density-matrix check
import orchestrator as l17_orch  # noqa: E402,F401  lesson 17: orchestrator, SPSA multistart
import solution_cache_key as l17_cache  # noqa: E402,F401
import solution_constrained as l13_mitigate  # noqa: E402,F401  lesson 13: constrained readout mitigation
import solution_distance as l19_distance  # noqa: E402,F401
import solution_fair as l18_fair  # noqa: E402,F401  lesson 18: fair harness
import solvers as l18_solvers  # noqa: E402,F401  lesson 18: greedy, annealing, exact
