"""Recomputes the numbers used in the L400 concept notes' worked examples (lessons 17-21) from the labs' own code.

Run: python L400_concept_examples.py   (about 1 minute; output kept in L400-concept-examples-output.txt)
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import sys

LABS = pathlib.Path(__file__).resolve().parents[1] / "labs" / "L400"


def run(lab, script, argv=()):
    folder = LABS / lab
    sys.path.insert(0, str(folder))
    old_argv, sys.argv = sys.argv, [script, *argv]
    try:
        spec = importlib.util.spec_from_file_location(f"ex_{lab[:2]}_{script[:-3]}", folder / script)
        module = importlib.util.module_from_spec(spec)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            spec.loader.exec_module(module)
            if hasattr(module, "main"):
                module.main(list(argv)) if script in ("app.py",) else module.main()
        return buffer.getvalue()
    finally:
        sys.argv = old_argv
        sys.path.remove(str(folder))
        for name in [n for n in sys.modules if n in ("app", "repository", "tenancy", "rollout", "migrations", "capacity",
                                                      "fines_service", "strangler", "traffic", "l300_log", "flags")]:
            del sys.modules[name]


if __name__ == "__main__":
    print("== 17 strangler: big bang vs shadow (2,000 seeded requests)")
    print(run("17-strangler-fig", "failure_lab.py"))
    print("== 18 tenancy: 50 libraries x 40 loans, shipped repository")
    print(run("18-multi-tenancy", "app.py"))
    print("== 19 policy: RBAC vs ABAC on 14 cases")
    print("\n".join(run("19-policy-as-code", "app.py", ["--solution"]).splitlines()[:2]))
    print("== 20 migrations: plans with the shipped and the fixed guard")
    print(run("20-evolutionary-migrations", "failure_lab.py"))
    print("== 21 capacity: options (solution sizing)")
    print(run("21-capacity-planning", "app.py", ["--solution"]))
    print(json.dumps({"note": "timings in 18 (ms) vary with the disk; everything else is seeded"}))
