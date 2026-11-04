"""Build task solution: a third driven adapter that keeps loans in a JSON file.

Nothing in domain.py, ports.py or the driving adapters changes; only app.py's DRIVEN map gains a line.
"""
import json
import pathlib

from domain import Loan


class JsonFileLoanStore:  # implements ports.ForStoringLoans
    def __init__(self, path):
        self._path = pathlib.Path(path)
        if not self._path.exists():
            self._write([])

    def _read(self):
        return [Loan(**row) for row in json.loads(self._path.read_text(encoding="utf-8"))]

    def _write(self, loans):
        self._path.write_text(json.dumps([vars(l) for l in loans], indent=1), encoding="utf-8")

    def add(self, book_id, member_id):
        loans = self._read()
        loan = Loan(len(loans) + 1, book_id, member_id)
        self._write(loans + [loan])
        return loan

    def get(self, loan_id):
        return next((l for l in self._read() if l.id == loan_id), None)

    def active(self):
        return [l for l in self._read() if not l.returned]

    def mark_returned(self, loan_id):
        loans = self._read()
        for loan in loans:
            if loan.id == loan_id:
                loan.returned = True
        self._write(loans)
