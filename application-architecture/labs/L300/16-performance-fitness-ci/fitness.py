"""Architecture fitness functions as CI gates (lesson 16 lab code). Run: python fitness.py  (exit 1 = a gate failed)

Each gate prints one JSON line {"gate", "ok", "value", "budget"}. Same ideas as import-linter contracts,
k6 thresholds and pytest-benchmark comparisons. `--solution` runs the gates on solution/loans_repo.py.
"""
import argparse
import ast
import importlib.util
import json
import pathlib
import sys
import timeit

import loans_repo
from http_api import start
from load_test import run_load

HERE = pathlib.Path(__file__).resolve().parent
QUERY_BUDGET = 2  # SQL statements per report - for 10 AND 500 loans: the count must not grow with the data
BENCH_BUDGET_MS = 50  # generous on purpose: timing gates must not flake on a busy CI runner
P95_BUDGET_MS = 200
FORBIDDEN = {"domain.py": {"sqlite3", "http", "urllib", "loans_repo", "http_api"}}  # domain stays pure


class QueryCounter:
    """Counts the SQL statements SQLite actually executes (sqlite3 trace callback)."""

    def __init__(self, conn):
        self.conn, self.statements = conn, []

    def __enter__(self):
        self.conn.set_trace_callback(self.statements.append)
        return self

    def __exit__(self, *exc):
        self.conn.set_trace_callback(None)


def gate_import_boundaries(folder=HERE):
    found = []
    for file, forbidden in FORBIDDEN.items():
        tree = ast.parse((folder / file).read_text(encoding="utf-8"))
        names = ({a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names} |
                 {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module})
        found += [f"{file} imports {name}" for name in sorted(names & forbidden)]
    return {"gate": "import-boundaries", "ok": not found, "value": found, "budget": "domain.py imports no adapters"}


def gate_query_count(repo):
    counts = {}
    for loans in (10, 500):
        conn = repo.seeded_db(loans=loans)
        with QueryCounter(conn) as counter:
            repo.overdue_report(conn)
        counts[loans] = len(counter.statements)  # deterministic: same data, same count, on every machine
    return {"gate": "query-count", "ok": max(counts.values()) <= QUERY_BUDGET, "value": counts, "budget": QUERY_BUDGET}


def gate_microbenchmark(repo):
    conn = repo.seeded_db(loans=500)
    runs = timeit.repeat(lambda: repo.overdue_report(conn), number=5, repeat=5)
    best_ms = min(runs) / 5 * 1000  # min() of the repeats: the least disturbed run (timeit docs)
    return {"gate": "micro-benchmark", "ok": best_ms <= BENCH_BUDGET_MS, "value": round(best_ms, 2),
            "budget": BENCH_BUDGET_MS}


def gate_response_time(repo):
    server, url = start(repo, loans=500)
    try:
        result = run_load(url + "/reports/overdue", users=4, requests_per_user=10)
    finally:
        server.shutdown()
        server.server_close()
    return {"gate": "response-time-p95", "ok": result["p95_ms"] <= P95_BUDGET_MS and result["errors"] == 0,
            "value": result, "budget": P95_BUDGET_MS}


def main(argv=None, out=sys.stdout):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--solution", action="store_true", help="check solution/loans_repo.py")
    repo = loans_repo
    if parser.parse_args(argv).solution:
        spec = importlib.util.spec_from_file_location("loans_repo_solution", HERE / "solution" / "loans_repo.py")
        repo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(repo)
    results = [gate_import_boundaries(), gate_query_count(repo), gate_microbenchmark(repo), gate_response_time(repo)]
    for result in results:
        print(json.dumps(result, sort_keys=True), file=out)
    failed = [r["gate"] for r in results if not r["ok"]]
    print("fitness: " + ("all gates passed" if not failed else "FAILED " + ", ".join(failed)), file=out)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
