"""Application service + demo: load the aggregate, call ONE method on the root, save it. Run: python app.py"""
from datetime import date

from member import LoanRuleViolation, Member
from member_repository import BookAlreadyOnLoan, SqliteMemberRepository


def borrow(repo, member_id, book_id, today):
    member = repo.get(member_id)
    member.borrow(book_id, today)  # the aggregate decides
    repo.save(member)  # the repository persists the whole aggregate in one transaction
    return member


def give_back(repo, member_id, book_id, today):
    member = repo.get(member_id)
    member.give_back(book_id, today)
    repo.save(member)
    return member


def attempt(label, action):
    try:
        member = action()
        print(f"{label:<22} -> ok, {len(member.active_loans)}/{member.max_loans} active, version {member.version}")
    except (LoanRuleViolation, BookAlreadyOnLoan) as exc:
        print(f"{label:<22} -> {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    repo, day = SqliteMemberRepository(), date(2026, 10, 1)
    repo.add(Member("m1", max_loans=3))
    repo.add(Member("m2", max_loans=3))
    attempt("m1 borrows b1", lambda: borrow(repo, "m1", "b1", day))
    attempt("m1 borrows b1 again", lambda: borrow(repo, "m1", "b1", day))
    attempt("m1 borrows b2", lambda: borrow(repo, "m1", "b2", day))
    attempt("m1 borrows b3", lambda: borrow(repo, "m1", "b3", day))
    attempt("m1 borrows b4", lambda: borrow(repo, "m1", "b4", day))
    attempt("m2 borrows b1", lambda: borrow(repo, "m2", "b1", day))
    attempt("m1 returns b1", lambda: give_back(repo, "m1", "b1", day))
    attempt("m2 borrows b1", lambda: borrow(repo, "m2", "b1", day))
    repo.close()
