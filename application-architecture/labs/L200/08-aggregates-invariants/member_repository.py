"""One repository per aggregate: members are loaded and saved WHOLE. There is no LoanRepository."""
import sqlite3
from datetime import date

from member import Loan, Member

SCHEMA = """
CREATE TABLE IF NOT EXISTS members (member_id TEXT PRIMARY KEY, max_loans INTEGER NOT NULL,
                                    version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS loans (member_id TEXT NOT NULL REFERENCES members(member_id), book_id TEXT NOT NULL,
                                  borrowed_on TEXT NOT NULL, returned_on TEXT);
-- rule ACROSS aggregates (two members, one book): enforced by the database, not by Member
CREATE UNIQUE INDEX IF NOT EXISTS one_active_loan_per_book ON loans(book_id) WHERE returned_on IS NULL;
"""


class MemberNotFound(KeyError):
    pass


class ConcurrencyConflict(Exception):
    pass


class BookAlreadyOnLoan(Exception):
    pass


class SqliteMemberRepository:
    def __init__(self, path=":memory:"):
        self._db = sqlite3.connect(path)
        self._db.executescript(SCHEMA)

    def add(self, member):
        with self._db:
            self._db.execute("INSERT INTO members VALUES (?, ?, 0)", (member.member_id, member.max_loans))

    def get(self, member_id):
        row = self._db.execute("SELECT max_loans, version FROM members WHERE member_id = ?", (member_id,)).fetchone()
        if row is None:
            raise MemberNotFound(member_id)
        loans = [Loan(b, date.fromisoformat(on), date.fromisoformat(back) if back else None)
                 for b, on, back in self._db.execute("SELECT book_id, borrowed_on, returned_on FROM loans "
                                                     "WHERE member_id = ? ORDER BY rowid", (member_id,))]
        return Member(member_id, row[0], loans, row[1])

    def save(self, member):
        try:
            with self._db:  # one transaction per aggregate: all of the member's rows, or none
                self._claim_version(member)
                self._db.execute("DELETE FROM loans WHERE member_id = ?", (member.member_id,))
                self._db.executemany("INSERT INTO loans VALUES (?, ?, ?, ?)", [
                    (member.member_id, l.book_id, l.borrowed_on.isoformat(),
                     l.returned_on.isoformat() if l.returned_on else None) for l in member.loans])
        except sqlite3.IntegrityError as exc:
            raise BookAlreadyOnLoan(f"another member has that book on loan ({exc})") from exc
        member.version += 1

    def _claim_version(self, member):
        cur = self._db.execute("UPDATE members SET version = version + 1 WHERE member_id = ? AND version = ?",
                               (member.member_id, member.version))
        if cur.rowcount != 1:  # someone saved this member since we loaded it
            raise ConcurrencyConflict(f"member {member.member_id} changed since version {member.version}")

    def close(self):
        self._db.close()
