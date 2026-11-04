"""Try it (lesson 8): two experiments on the consistency boundary. Run: python try_it.py"""
from datetime import date

from member import Member
from member_repository import ConcurrencyConflict, SqliteMemberRepository

DAY = date(2026, 10, 1)


class NaiveRepository(SqliteMemberRepository):
    """Same repository with the version check switched off (last write wins)."""

    def _claim_version(self, member):
        self._db.execute("UPDATE members SET version = version + 1 WHERE member_id = ?", (member.member_id,))


def two_tabs(repo):
    repo.add(Member("m1", max_loans=3))
    setup = repo.get("m1")
    setup.borrow("b1", DAY)
    setup.borrow("b2", DAY)
    repo.save(setup)
    tab_a, tab_b = repo.get("m1"), repo.get("m1")  # two requests load the same member (2 of 3 loans)
    tab_a.borrow("b3", DAY)
    tab_b.borrow("b4", DAY)  # each copy alone respects the limit
    repo.save(tab_a)
    try:
        repo.save(tab_b)
    except ConcurrencyConflict as exc:
        return f"ConcurrencyConflict: {exc}"
    saved = repo.get("m1")
    return f"saved; stored loans: {[l.book_id for l in saved.active_loans]} (limit {saved.max_loans})"


def try_1_two_tabs():
    print(f"[1] with version check    -> {two_tabs(SqliteMemberRepository())}")
    print(f"[1] without version check -> {two_tabs(NaiveRepository())}")


def try_2_rule_without_the_index():
    repo = SqliteMemberRepository()
    repo._db.execute("DROP INDEX one_active_loan_per_book")  # remove the cross-aggregate guard
    for member_id in ("m1", "m2"):
        repo.add(Member(member_id))
        member = repo.get(member_id)
        member.borrow("b1", DAY)
        repo.save(member)
    rows = repo._db.execute("SELECT member_id FROM loans WHERE book_id = 'b1' AND returned_on IS NULL").fetchall()
    print(f"[2] no unique index: b1 is on loan to {[r[0] for r in rows]} at the same time")


if __name__ == "__main__":
    try_1_two_tabs()
    try_2_rule_without_the_index()
