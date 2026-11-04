"""Try it (lesson 16): which report is faster in-process, and what the import gate says about a planted import.

Run: python try_it.py   (scratch copy in .tryit-work/, deleted after)
"""
import shutil
import time
import timeit

import fitness
import loans_repo as base
from failure_lab import HERE, load

WORK = HERE / ".tryit-work"


def try_1_microbenchmark():
    solution = load(HERE / "solution" / "loans_repo.py", "loans_repo_solution")
    result = {}
    for label, repo in [("N+1", base), ("JOIN", solution)]:
        conn = repo.seeded_db(loans=500)
        result[label] = round(min(timeit.repeat(lambda: repo.overdue_report(conn), number=5, repeat=5)) / 5 * 1000, 2)
    print(f"[1] in-process SQLite, 500 loans, best of 5 x 5 (ms per report): {result}")


def try_2_planted_import():
    WORK.mkdir(exist_ok=True)
    text = (HERE / "domain.py").read_text(encoding="utf-8")
    (WORK / "domain.py").write_text("import sqlite3  # 'just a quick lookup'\n" + text, encoding="utf-8")
    print(f"[2] domain.py imports sqlite3 -> {fitness.gate_import_boundaries(WORK)}")


if __name__ == "__main__":
    try:
        try_1_microbenchmark()
        try_2_planted_import()
    finally:
        for _ in range(5):  # retry: some network mounts need a second pass
            shutil.rmtree(WORK, ignore_errors=True)
            if not WORK.exists():
                break
            time.sleep(0.5)
