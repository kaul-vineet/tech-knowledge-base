"""Build-task solution: a control counts only if every test it names EXISTS (and, with --run, PASSES), every element
has at least one threat, and every flow that crosses a trust boundary has Tampering and Information-disclosure threats.
Unverified controls do not close attack-tree leaves."""
import os
import random
import subprocess
import sys
from collections import defaultdict

import threat_model as tm
from threat_model import cheapest, inject_drift, load, test_exists  # noqa: F401


def check(model) -> list:
    problems = tm.check(model)
    for cid, c in sorted(model["controls"].items()):
        problems += [f"{cid}: test missing {ref}" for ref in c["tests"] if not test_exists(ref)]
        if not c["tests"]:
            problems.append(f"{cid}: no test proves this control")
    covered = defaultdict(set)
    for t in model["threats"]:
        covered[t["element"]].add(t["stride"])
    for name, e in model["elements"].items():
        if not covered[name]:
            problems.append(f"{name}: no threats modelled")
        if e["type"] == "flow" and tm.crosses_boundary(model, e):
            problems += [f"{name}: boundary-crossing flow lacks {c}" for c in "TI" if c not in covered[name]]
    return problems


def verified_controls(model) -> set:
    return {cid for cid, c in model["controls"].items() if c["tests"] and all(test_exists(r) for r in c["tests"])}


def run_control_tests(model) -> dict:
    """Run each referenced test (one unittest process per test file, from the test's own folder)."""
    by_file = defaultdict(list)
    for cid, c in model["controls"].items():
        for ref in c["tests"]:
            file, cls, meth = ref.split("::")
            by_file[file].append((cid, f"{file.rsplit('/', 1)[1][:-3]}.{cls}.{meth}"))
    env = {k: v for k, v in os.environ.items() if k not in ("BUILD_TARGET", "BUILD_IMPL")}
    result = {}
    for file, items in sorted(by_file.items()):
        r = subprocess.run([sys.executable, "-m", "unittest", *[name for _, name in items]], cwd=tm.TOPIC / file.rsplit("/", 1)[0],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, env=env)
        for cid, _ in items:
            result[cid] = result.get(cid, True) and r.returncode == 0
    return result


if __name__ == "__main__":
    m = load()
    print("clean model problems:", check(m), "| verified controls:", len(verified_controls(m)), "of", len(m["controls"]))
    victim = inject_drift(m, random.Random(tm.SEED))
    print("after drift:")
    for p in check(m):
        print("  -", p)
    cost, path = cheapest(m["attack_tree"], verified_controls(m))
    print(f"cheapest open attack path with only VERIFIED controls: cost {cost} via {path}")
    if "--run" in sys.argv:
        print("referenced tests pass:", run_control_tests(load()))
