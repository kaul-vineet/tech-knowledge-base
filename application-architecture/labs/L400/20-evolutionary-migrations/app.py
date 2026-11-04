"""Lesson 20 demo: big-bang schema change vs expand/contract during a rolling deploy; fitness history.

Run: python app.py [--solution]   writes out/fitness.jsonl, then: python dashboard.py
"""
import argparse
import importlib.util
import json
import pathlib

import migrations
import rollout

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_plans(module, history):
    results = {}
    for plan in (rollout.big_bang, rollout.expand_contract):
        r, rows = plan(module)
        for row in rows:
            row["plan"] = plan.__name__
        with open(history, "a", encoding="utf-8") as f:
            f.writelines(json.dumps(row) + "\n" for row in rows)
        results[plan.__name__] = (r, rows)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", action="store_true")
    module = load(HERE / "solution" / "migrations.py", "migrations_solution") \
        if parser.parse_args(argv).solution else migrations
    (HERE / "out").mkdir(exist_ok=True)
    history = HERE / "out" / "fitness.jsonl"
    history.write_text("", encoding="utf-8")
    for name, (r, rows) in run_plans(module, history).items():
        print(f"{name:16}: {r.errors} failed requests of {100 * len(rows) if name == 'expand_contract' else 100}; "
              f"first error: {r.log[0] if r.log else '-'}")
    print("history: out/fitness.jsonl (python dashboard.py)")


if __name__ == "__main__":
    main()
