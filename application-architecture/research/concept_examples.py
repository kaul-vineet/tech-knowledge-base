"""Computes every worked-example value used in content/concepts/*.md by running the lab code.

Run from the domain folder:  python research/concept_examples.py
Output is saved in research/concept-examples-output.txt. Each snippet runs in its own
subprocess with the lab folder as cwd, because labs 2 and 5 both have a module named app.py.
"""
import pathlib
import subprocess
import sys
import textwrap

LABS = pathlib.Path(__file__).resolve().parent.parent / "labs" / "L100"

EXAMPLES = {
    "01-setup-workspace": """
        import re, subprocess, sys, pathlib
        for lab in sorted(p for p in pathlib.Path('..').iterdir() if p.name[:2].isdigit()):
            out = subprocess.run([sys.executable, '-m', 'unittest', 'discover'], cwd=lab,
                                 capture_output=True, text=True).stderr
            print(lab.name, re.search(r'Ran (\\d+) test', out).group(1), 'tests')
        print('lab 02 breakdown: 5 rule tests x 2 repositories + 1 HTTP + 1 dependency =', 5 * 2 + 1 + 1)
    """,
    "02-layered-structure": """
        from repository import SqliteLoanRepository
        from service import LoanService, LoanLimitReached
        repo = SqliteLoanRepository(':memory:')
        svc = LoanService(repo)  # default max_active_per_member=3
        for book in ('b1', 'b2', 'b3'):
            print('borrow', book, '-> loan id', svc.borrow(book, 'm1').id)
        try:
            svc.borrow('b4', 'm1')
        except LoanLimitReached as exc:
            print('borrow b4 ->', type(exc).__name__, '-', exc)
        print('give back loan 2 -> returned =', svc.give_back(2).returned)
        print('borrow b4 -> loan id', svc.borrow('b4', 'm1').id)
        print('active rows:', [(l.id, l.book_id) for l in repo.active()])
        evil = "x'); DROP TABLE loans;--"
        print('placeholder-bound evil bookId stored as text, id', svc.borrow(evil, 'm2').id)
        print('table still exists, rows =', repo._db.execute('SELECT COUNT(*) FROM loans').fetchone()[0])
    """,
    "03-modular-monolith": """
        import ast
        from check_boundaries import imported_targets, violations
        src = 'from ..catalog.internal import store'
        print('file package: library.loans, statement:', src)
        print('resolved targets:', list(imported_targets(ast.parse(src), 'library.loans')))
        print('violations:', violations(src, 'library.loans', 'library/loans/service.py'))
        print('public import ok:', violations('from library import catalog', 'library.loans'))
    """,
    "04-api-first-openapi": """
        from contract_check import check, find_operation, load_spec
        spec = load_spec()
        print('openapi =', spec['openapi'])
        print('GET /loans/42 matches template:', find_operation(spec, 'GET', '/loans/42')[0])
        n = sum(len(op['responses']) for item in spec['paths'].values() for op in item.values())
        print('declared (operation, status) pairs:', n)
        body = {'id': '7', 'bookId': 'b1', 'status': 'lost'}
        for p in check(spec, 'GET', '/loans/7', 200, body):
            print('problem:', p)
        print('status 422 on POST /loans:', check(spec, 'POST', '/loans', 422, {}))
    """,
    "05-config-12factor": """
        from config import ConfigError, load_settings
        try:
            load_settings({'LOANS_PORT': '70000', 'LOANS_LOG_LEVEL': 'warn'})
        except ConfigError as exc:
            print('ConfigError:', exc)
        print(load_settings({'LOANS_PORT': '9000', 'LOANS_LOG_LEVEL': 'warning',
                             'LOANS_SMTP_PASSWORD': 'example-only'}))
    """,
    "06-documenting-architecture": """
        import re
        from check_docs import DOCS, MERMAID_ELEMENT, MERMAID_REL, DSL_ELEMENT, DSL_REL
        for name in ('c4-context.mmd', 'c4-container.mmd'):
            text = (DOCS / name).read_text()
            print(name, 'elements:', MERMAID_ELEMENT.findall(text), 'relationships:', len(MERMAID_REL.findall(text)))
        dsl = (DOCS / 'workspace.dsl').read_text()
        parent = {'api': 'loans', 'db': 'loans'}  # containers declared inside softwareSystem loans
        rels = DSL_REL.findall(dsl)
        print('DSL relationships:', rels)
        implied = sorted({(parent.get(a, a), parent.get(b, b)) for a, b in rels
                          if parent.get(a, a) != parent.get(b, b)})
        print('system-level (implied) relationships for the context view:', implied)
        numbers = [int(m) for m in re.findall(r'adr-(\\d+)', ' '.join(p.name for p in DOCS.iterdir()))]
        print('next ADR file: adr-%03d-<title>.md' % (max(numbers) + 1))
    """,
}

for lab, code in EXAMPLES.items():
    print(f"== {lab}")
    result = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=LABS / lab,
                            capture_output=True, text=True)
    print(result.stdout.rstrip() or result.stderr)
