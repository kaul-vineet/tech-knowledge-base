"""Compute the worked-example numbers quoted in content/concepts/L200/*.md (run from the topic folder).

    python research/L200_concept_examples.py > research/L200-concept-examples-output.txt
"""
import ast
import importlib
import pathlib
import sys
from datetime import date

LABS = pathlib.Path(__file__).resolve().parents[1] / "labs" / "L200"


def use(lab):
    """Import a lab's modules from its folder (each lab is self-contained, some module names repeat)."""
    for name in ("app", "domain", "ports", "outbox", "events", "loans", "member", "member_repository"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(LABS / lab))


def lesson7():
    use("07-hexagonal-architecture")
    tree = ast.parse((LABS / "07-hexagonal-architecture" / "domain.py").read_text(encoding="utf-8"))
    imports = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} |
                     {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names})
    app = importlib.import_module("app")
    results = {}
    for storage in ("memory", "sqlite"):
        service = app.build(storage)
        results[storage] = (app.cli(service, "borrow", "b1", "m1")[0], app.cli(service, "borrow", "b1", "m2"))
    print(f"[7] domain.py imports: {imports}")
    print(f"[7] same CLI calls on both driven adapters: {results}")


def lesson8():
    use("08-aggregates-invariants")
    from member import Member
    from member_repository import ConcurrencyConflict, SqliteMemberRepository
    repo, day = SqliteMemberRepository(), date(2026, 10, 1)
    repo.add(Member("m1"))
    m = repo.get("m1")
    m.borrow("b1", day)
    m.borrow("b2", day)
    repo.save(m)
    a, b = repo.get("m1"), repo.get("m1")
    a.borrow("b3", day)
    b.borrow("b4", day)
    repo.save(a)
    try:
        repo.save(b)
    except ConcurrencyConflict as exc:
        print(f"[8] both copies loaded at version {b.version}; A saved -> version {a.version}; B -> {exc}")


def lesson9():
    use("09-event-driven-integration")
    from bus import InProcessBus
    from outbox import LoansWithOutbox
    loans = LoansWithOutbox()
    loans.borrow("b1", "m1")
    loans.give_back(1)
    rows = loans.db.execute("SELECT seq, channel FROM outbox").fetchall()
    print(f"[9] borrow + return -> outbox rows {rows}, loans rows "
          f"{loans.db.execute('SELECT COUNT(*) FROM loans').fetchone()[0]}")
    import try_it
    try_it.try_1_crash_between_publish_and_mark()
    del InProcessBus


def lesson10():
    use("10-oidc-authentication")
    from id_token_rules import validate_claims
    from mock_idp import s256
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    print(f"[10] PKCE: verifier ({len(verifier)} chars) -> challenge {s256(verifier)}")
    now = 1_800_000_000
    claims = {"iss": "https://idp", "sub": "m1", "aud": "library-web", "iat": now - 400, "nonce": "n1"}
    for exp in (now - 59, now - 61):
        print(f"[10] exp = now{exp - now:+d} s, leeway 60 -> {validate_claims({**claims, 'exp': exp}, issuer='https://idp', client_id='library-web', nonce='n1', now=now)}")


def lesson11():
    use("11-testing-pyramid")
    import pyramid
    rows = {name: pyramid.run_layer(pattern) for name, pattern in pyramid.LAYERS}
    print("[11] " + ", ".join(f"{n}: {r['tests']} tests, mean {r['mean_ms']:.2f} ms" for n, r in rows.items()))


if __name__ == "__main__":
    lesson7()
    lesson8()
    lesson9()
    lesson10()
    lesson11()
