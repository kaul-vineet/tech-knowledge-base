"""Fitness dashboard: read the JSON-lines history and judge every step against its threshold.

Run: python dashboard.py [--plan expand_contract] [--file out/fitness.jsonl]   (exit 1 = a step broke a fitness function)
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
THRESHOLDS = {"errors": 0, "flags_expired": 0}  # metric -> highest allowed value at every step


def judge(rows):
    return [(row, [f"{k}={row[k]} > {limit}" for k, limit in THRESHOLDS.items() if row[k] > limit]) for row in rows]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan")
    parser.add_argument("--file", default=HERE / "out" / "fitness.jsonl")
    args = parser.parse_args(argv)
    rows = [json.loads(line) for line in pathlib.Path(args.file).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if not args.plan or r["plan"] == args.plan]
    print(f"{'plan / step':66} {'fleet':10} {'errors':>6} {'unbackfilled':>12}  columns")
    broken = 0
    for row, problems in judge(rows):
        broken += bool(problems)
        print(f"{row['plan'] + ' / ' + row['step']:66} {row['fleet']:10} {row['errors']:>6} "
              f"{str(row['unbackfilled']):>12}  {','.join(row['columns'])}{'  <-- ' + '; '.join(problems) if problems else ''}")
    print(f"{len(rows)} steps, {broken} broke a fitness function")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
