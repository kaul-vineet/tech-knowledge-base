"""Lesson 20 failureLab: the contract step runs as soon as the backfill is done, while v2 instances still write name.

Run: python failure_lab.py
"""
import migrations as base
import rollout
from app import HERE, load


def main():
    solution = load(HERE / "solution" / "migrations.py", "migrations_solution")
    for label, module in [("base    ", base), ("solution", solution)]:
        r, rows = rollout.expand_contract(module)
        attempt = next(row for row in rows if row["step"].startswith("try contract"))
        print(f"{label}: {attempt['step']} with fleet {attempt['fleet']} -> {r.errors} failed requests of 700"
              + (f"; first: {r.log[0]}" if r.log else ""))
    r, _ = rollout.big_bang(base)
    print(f"big bang: schema changed in one step -> {r.errors} failed requests of 100; first: {r.log[0]}")


if __name__ == "__main__":
    main()
