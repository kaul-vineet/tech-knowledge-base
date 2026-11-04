"""Try it (lesson 7): two experiments on the hexagon. Run: python try_it.py (never edits the lab files)."""
import os
import pathlib
import shutil
import subprocess
import sys
import time

from domain import LoanService
from ports import ForStoringLoans

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / ".tryit-work"


def remove_scratch():
    for _ in range(5):  # retry: some network mounts need a second pass
        shutil.rmtree(WORK, ignore_errors=True)
        if not WORK.exists():
            return
        time.sleep(0.5)


def try_1_domain_imports_sqlite():
    remove_scratch()
    WORK.mkdir()
    for path in HERE.glob("*.py"):
        shutil.copyfile(path, WORK / path.name)
    domain = WORK / "domain.py"
    domain.write_text(domain.read_text(encoding="utf-8").replace(
        "from dataclasses import dataclass", "import sqlite3\nfrom dataclasses import dataclass", 1), encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "unittest", "test_hexagon.DependencyRuleTest"], cwd=WORK,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                         capture_output=True, text=True, encoding="utf-8")
    detail = next(line for line in run.stderr.splitlines() if line.startswith("AssertionError")).split(" : ")[-1]
    print(f"[1] domain.py imports sqlite3 -> {run.stderr.strip().splitlines()[-1]}: {detail}")


class HalfStore:
    """An adapter someone forgot to finish: no mark_returned."""

    def __init__(self):
        self.rows = []

    def add(self, book_id, member_id):
        from domain import Loan
        self.rows.append(Loan(len(self.rows) + 1, book_id, member_id))
        return self.rows[-1]

    def get(self, loan_id):
        return next((r for r in self.rows if r.id == loan_id), None)

    def active(self):
        return [r for r in self.rows if not r.returned]


def try_2_half_adapter():
    store = HalfStore()
    print(f"[2] isinstance(HalfStore(), ForStoringLoans) -> {isinstance(store, ForStoringLoans)}")
    loans = LoanService(store)  # Python does not check the port here
    print(f"[2] borrow b1 -> loan {loans.borrow('b1', 'm1').id} (still works)")
    try:
        loans.give_back(1)
    except AttributeError as exc:
        print(f"[2] give_back(1) -> AttributeError: {exc}")


if __name__ == "__main__":
    try:
        try_1_domain_imports_sqlite()
        try_2_half_adapter()
    finally:
        remove_scratch()
