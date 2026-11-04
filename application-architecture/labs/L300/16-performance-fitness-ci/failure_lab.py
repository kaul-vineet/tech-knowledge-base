"""Lesson 16 failureLab: a refactor turned one JOIN into N+1 queries. Which gate notices?

Run: python failure_lab.py   (base loans_repo.py vs solution/loans_repo.py)
"""
import importlib.util
import pathlib
import time

import loans_repo as base
from fitness import QueryCounter, gate_query_count, gate_response_time

HERE = pathlib.Path(__file__).resolve().parent
ROUND_TRIP_S = 0.0005  # >= 0.5 ms per statement (sleep overshoots): a database on the network instead of in-process SQLite


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def with_round_trips(repo, loans=500):
    conn = repo.seeded_db(loans=loans)
    conn.set_trace_callback(lambda statement: time.sleep(ROUND_TRIP_S))  # runs once per executed statement
    started = time.perf_counter()
    repo.overdue_report(conn)
    return round((time.perf_counter() - started) * 1000, 1)


def main():
    solution = load(HERE / "solution" / "loans_repo.py", "loans_repo_solution")
    conn = base.seeded_db(loans=500)
    same = base.overdue_report(conn) == solution.overdue_report(conn)
    print(f"same report rows (unit-test view): {same}, {len(solution.overdue_report(conn))} overdue loans")
    for label, repo in [("base     (after refactor)", base), ("solution (one JOIN)     ", solution)]:
        conn = repo.seeded_db(loans=10)
        with QueryCounter(conn) as counter:
            repo.overdue_report(conn)
        query, timing = gate_query_count(repo), gate_response_time(repo)
        print(f"{label}: query-count {query['value']} -> {'PASS' if query['ok'] else 'FAIL'}; "
              f"p95 {timing['value']['p95_ms']} ms -> {'PASS' if timing['ok'] else 'FAIL'}; "
              f"with 0.5 ms round trips: {with_round_trips(repo)} ms per report")
        print(f"    trace (10 loans), first 3: {[' '.join(sql.split()) for sql in counter.statements[:3]]}")


if __name__ == "__main__":
    main()
