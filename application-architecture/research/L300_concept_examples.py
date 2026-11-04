"""Compute the worked-example numbers quoted in content/concepts/L300/*.md (run from the topic folder).

    python research/L300_concept_examples.py > research/L300-concept-examples-output.txt
Deterministic parts only (seeded data, query counts, burn rates); timings live in the lab READMEs as ranges.
"""
import importlib
import importlib.util
import pathlib
import sys

LABS = pathlib.Path(__file__).resolve().parents[1] / "labs" / "L300"
SHARED = ("app", "failure_lab", "projector", "write_model", "resilience", "deps", "loans_service", "contract",
          "provider", "consumer", "slo", "traffic", "fitness", "loans_repo", "domain", "http_api", "load_test",
          "test_consumer", "try_it")


def use(lab):
    """Import a lab's modules from its folder (each lab is self-contained; module names repeat across labs)."""
    for name in SHARED:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(LABS / lab))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lesson12():
    use("12-cqrs-read-models")
    fl = importlib.import_module("failure_lab")
    solution = load(LABS / "12-cqrs-read-models" / "solution" / "projector.py", "p12")
    for label, module in (("base", fl.base), ("solution", solution)):
        store, projector, crashed, last = fl.crash_and_restart(module)
        print(f"[12] {label}: {crashed}; position {projector.position()}/{last}; "
              f"drift {module.drift(store, projector.db, module.Projector)}")
    try_it = importlib.import_module("try_it")
    try_it.try_2_half_fix()


def lesson13():
    use("13-resilience-patterns")
    fl = importlib.import_module("failure_lab")
    from deps import Catalogue
    solution = load(LABS / "13-resilience-patterns" / "solution" / "loans_service.py", "s13")
    for label, module in (("shared pool 8", fl.base), ("bulkheads 4+4", solution)):
        records = fl.run_waves(module, Catalogue(mode="slow"))
        print(f"[13] {label}: {sum(r['ok'] for r in records)}/{len(records)} ok; {fl.summary(records)}")


def lesson14():
    use("14-consumer-driven-contracts")
    fl = importlib.import_module("failure_lab")
    solution = load(LABS / "14-consumer-driven-contracts" / "solution" / "contract.py", "c14")
    for label, verifier in (("status only", fl.base), ("body + matchers", solution)):
        print(f"[14] rename title->name, {label}: {fl.checks(verifier)}")


def lesson15():
    use("15-slo-error-budgets")
    fl = importlib.import_module("failure_lab")
    solution = fl.load(LABS / "15-slo-error-budgets" / "solution" / "slo.py", "s15")
    report, problems, fired = fl.check(solution)
    burn = fired[0]["burn_long"]
    print(f"[15] last hour: {report}; base problems {fl.check(fl.base)[1]}; solution alerts {fired}")
    print(f"[15] budget used in 1 h = {burn} x 1/720 = {burn / 720:.2%}; "
          f"workbook time-to-fire = (1-0.99)/{burn / 100:.3f} x 60 min x 14.4 = {0.01 / (burn / 100) * 60 * 14.4:.1f} min")


def lesson16():
    use("16-performance-fitness-ci")
    fitness = importlib.import_module("fitness")
    solution = load(LABS / "16-performance-fitness-ci" / "solution" / "loans_repo.py", "r16")
    for label, repo in (("N+1", importlib.import_module("loans_repo")), ("JOIN", solution)):
        print(f"[16] {label}: query-count {fitness.gate_query_count(repo)['value']}")


if __name__ == "__main__":
    lesson12()
    lesson13()
    lesson14()
    lesson15()
    lesson16()
