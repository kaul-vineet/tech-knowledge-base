"""Lesson 15 failureLab: 20% of POST /loans become 2.4-3 s slow from 10:30 UTC. Mean vs latency SLI at 12:00.

Run: python failure_lab.py   (in-memory log; app.py writes the same log to out/requests.jsonl)
"""
import importlib.util
import pathlib

import slo as base
from traffic import END, lines

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(module, incident=True, now=END.timestamp()):
    records = module.parse(lines(incident=incident))
    return module.latency_report(records, now), module.latency_problems(records, now), module.alerts(records, now)


def main():
    solution = load(HERE / "solution" / "slo.py", "slo_solution")
    report = check(base)[0]
    print(f"last hour  : mean {report['mean']} ms, p95 {report['p95']} ms, p99 {report['p99']} ms")
    for label, module in [("base     slo.py (mean <= 200 ms)", base), ("solution slo.py (latency SLI)", solution)]:
        _, problems, fired = check(module)
        print(f"{label}: latency problems {problems or 'none'}; alerts {fired or 'none'}")


if __name__ == "__main__":
    main()
