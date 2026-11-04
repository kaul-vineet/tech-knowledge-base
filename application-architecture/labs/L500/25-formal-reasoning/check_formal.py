"""Numerical checks for the lesson 25 theorems. Run: python check_formal.py  (exit 0 = every check holds)."""
import random
import sys

import contracts as c
import model_check as mc

FAILURES = []


def check(label, ok):
    print(f"  [{'OK' if ok else 'FAIL'}] {label}")
    if not ok:
        FAILURES.append(label)


def theorem_invariant(rng):
    print("T1 invariant induction: Inv(initial) and every operation preserves Inv => Inv in every reachable state")
    check("base case: a new Member satisfies Inv", c.invariant(c.Member("m0")))
    s = c.random_traces(rng)
    print(f"      {s['calls']:,} random calls on the real L200 #8 Member aggregate, {s['rejected']:,} rejected by rules")
    check(f"Inv broken after {s['inv_broken']} calls", s["inv_broken"] == 0)
    check(f"borrow postcondition broken {s['post_broken']} times", s["post_broken"] == 0)
    check(f"rejected calls that changed state: {s['not_atomic']}", s["not_atomic"] == 0)
    check("loans is exposed as a read-only tuple (no append behind the root's back)",
          isinstance(c.Member("m9").loans, tuple))


def theorem_liskov():
    print("T2 Liskov rule: weaker-or-equal precondition and stronger-or-equal postcondition => safe substitution")
    expected = {"StrictLimit": (0, 0), "GenerousLimit": (0, 8), "NoOverdueAccepted": (33, 0)}
    for impl in (c.StrictLimit(), c.GenerousLimit(), c.NoOverdueAccepted()):
        name = type(impl).__name__
        pre_b, post_b = c.substitution_violations(impl)
        outcome = [c.client_borrow_up_to_limit(impl, overdue) for overdue in (0, 1)]
        print(f"      {name:<18} pre broken at {pre_b:>2} of {len(c.DOMAIN)} points, post broken at {post_b:>2}; "
              f"supertype client (overdue 0 / 1) ends with: {outcome}")
        check(f"{name}: violations {(pre_b, post_b)} as predicted {expected[name]}", (pre_b, post_b) == expected[name])
    check("the client written for the supertype stays within 3 loans only with the valid subtype",
          c.client_borrow_up_to_limit(c.StrictLimit()) <= 3 and c.client_borrow_up_to_limit(c.GenerousLimit()) > 3)


def theorem_model_checking():
    print("T3 BFS model checking: explores every reachable state; the first violation found has a shortest trace")
    n_bug, cex, _, _ = mc.bfs(fixed=False)
    brute = mc.shortest_by_enumeration(fixed=False)
    print(f"      buggy check-then-act: violation after exploring {n_bug} states; counterexample: {cex}")
    check(f"BFS counterexample length {len(cex)} = brute-force minimum {brute}", cex is not None and len(cex) == brute)
    n_fix, cex_fix, dead, _ = mc.bfs(fixed=True)
    check(f"atomic conditional insert: {n_fix} reachable states, no violation, {len(dead)} deadlocks",
          cex_fix is None and not dead and mc.shortest_by_enumeration(fixed=True) is None)
    ok, n = mc.can_always_free_book(fixed=True)
    check(f"AG EF book available: from all {n} reachable states the book can become free again", ok)
    counts = {k: (mc.reachable_states(False, tuple("ABCDEF"[:k])), mc.reachable_states(True, tuple("ABCDEF"[:k])))
              for k in range(2, 7)}
    print(f"      state explosion, members -> (buggy, fixed) reachable states: {counts}")
    check("buggy = 3^n and fixed = (n + 2) * 2^(n - 1) for n = 2..6",
          all(b == 3 ** k and f == (k + 2) * 2 ** (k - 1) for k, (b, f) in counts.items()))


if __name__ == "__main__":
    theorem_invariant(random.Random(2500))
    theorem_liskov()
    theorem_model_checking()
    print("ALL CHECKS OK" if not FAILURES else f"FAILED: {FAILURES}")
    sys.exit(1 if FAILURES else 0)
