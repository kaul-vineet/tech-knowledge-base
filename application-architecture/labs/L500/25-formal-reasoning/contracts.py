"""Lesson 25 - contracts: invariants of the real Member aggregate (L200 #8) and Liskov's substitution rule.

The aggregate is imported from labs/L200/08-aggregates-invariants/member.py, unchanged.
"""
import pathlib
import random
import sys
from datetime import date, timedelta

AGGREGATE_LAB = pathlib.Path(__file__).resolve().parents[2] / "L200" / "08-aggregates-invariants"
sys.path.insert(0, str(AGGREGATE_LAB))
sys.dont_write_bytecode = True  # read the L200 lab without leaving a __pycache__ in it
from member import LoanRuleViolation, Member  # noqa: E402

BOOKS = [f"b{i}" for i in range(1, 7)]


def invariant(member):
    """Inv: at most max_loans active loans, and no book twice among the active loans."""
    active = [loan.book_id for loan in member.active_loans]
    return len(active) <= member.max_loans and len(active) == len(set(active))


def snapshot(member):
    return tuple(member.loans), member.version


def random_traces(rng, traces=20_000, max_len=30):
    """Run random borrow/give_back sequences; check Inv after every call, the borrow postcondition on success,
    and failure atomicity (a rejected call leaves the state unchanged)."""
    stats = {"calls": 0, "rejected": 0, "inv_broken": 0, "post_broken": 0, "not_atomic": 0}
    for _ in range(traces):
        member, day = Member("m1", max_loans=3), date(2026, 10, 1)
        for _ in range(rng.randint(1, max_len)):
            op, book = rng.choice(["borrow", "give_back"]), rng.choice(BOOKS)
            day += timedelta(days=1)
            before, n_before = snapshot(member), len(member.active_loans)
            stats["calls"] += 1
            try:
                getattr(member, op)(book, day)
            except LoanRuleViolation:
                stats["rejected"] += 1
                stats["not_atomic"] += snapshot(member) != before
            else:
                if op == "borrow":
                    ok = len(member.active_loans) == n_before + 1 and book in [x.book_id for x in member.active_loans]
                    stats["post_broken"] += not ok
            stats["inv_broken"] += not invariant(member)
    return stats


# ---- Liskov substitution on a small, finite specification ----------------------------------------------
# Supertype LoanLimit.allowed(active, overdue):
#   pre_T : 0 <= active <= 10 and 0 <= overdue <= 3                     (any member record)
#   post_T: result => active < 3        (never allows a 4th loan)
#           active == 0 and overdue == 0 => result   (a new member in good standing can always borrow)
DOMAIN = [(a, o) for a in range(11) for o in range(4)]


def pre_T(active, overdue):
    return 0 <= active <= 10 and 0 <= overdue <= 3


def post_T(active, overdue, result):
    return (not result or active < 3) and (not (active == 0 and overdue == 0) or result)


class StrictLimit:            # stronger postcondition (allows less), same precondition -> a valid subtype
    def allowed(self, active, overdue):
        return active < 2 and overdue == 0


class GenerousLimit:          # weaker postcondition: allows a 4th and 5th loan -> NOT a subtype
    def allowed(self, active, overdue):
        return active < 5


class NoOverdueAccepted:      # stronger precondition: rejects inputs the supertype accepts -> NOT a subtype
    def allowed(self, active, overdue):
        if overdue > 0:
            raise ValueError("members with overdue loans are not accepted")
        return active < 3


def substitution_violations(impl):
    """Count domain points where pre_T holds but the subtype refuses the call (pre weakening broken)
    or returns a result that breaks post_T (post strengthening broken)."""
    pre_broken = post_broken = 0
    for active, overdue in DOMAIN:
        if not pre_T(active, overdue):
            continue
        try:
            result = impl.allowed(active, overdue)
        except ValueError:
            pre_broken += 1
            continue
        post_broken += not post_T(active, overdue, result)
    return pre_broken, post_broken


def client_borrow_up_to_limit(policy, overdue=0):
    """A client written against the supertype spec: keeps borrowing while allowed, relying on post_T.
    Returns the final number of active loans, or the error it hit."""
    active = 0
    try:
        while policy.allowed(active, overdue) and active < 10:
            active += 1
    except ValueError as exc:
        return f"error: {exc}"
    return active
