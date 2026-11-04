"""Local structural lint for architecture docs (NOT a renderer). Run: python check_docs.py

- ADRs follow Michael Nygard's sections: Title, Context, Decision, Status, Consequences.
- Mermaid C4 / Structurizr DSL: brackets balance and every relationship uses defined ids.
Real syntax validation happens in CI (mermaid-cli, structurizr validate).
"""
import pathlib
import re
import sys

DOCS = pathlib.Path(__file__).parent / "doc" / "arch"
ADR_SECTIONS = ["## Context", "## Decision", "## Status", "## Consequences"]
ADR_STATUSES = ("Proposed", "Accepted", "Deprecated", "Superseded")
MERMAID_ELEMENT = re.compile(r"^\s*(?:Person|System|Container|Component)\w*\((\w+)", re.M)
MERMAID_REL = re.compile(r"^\s*(?:Bi)?Rel\w*\((\w+),\s*(\w+)", re.M)
DSL_ELEMENT = re.compile(r"^\s*(\w+)\s*=\s*(person|softwareSystem|container)\b", re.M)
DSL_REL = re.compile(r"^\s*(\w+)\s*->\s*(\w+)", re.M)
DSL_VIEW = re.compile(r"^\s*(?:systemContext|container)\s+(\w+)\s+\"", re.M)


def balanced(text, pairs=("()", "{}")):
    text = re.sub(r'"[^"\n]*"', '""', text)  # ignore brackets inside quoted labels
    return all(text.count(o) == text.count(c) for o, c in pairs)


# ADR: Nygard sections in order; a reversed decision is marked Superseded, never deleted
def check_adr(text):
    problems = [] if re.match(r"# ADR \d+: \S", text) else ["title must look like '# ADR 1: Short noun phrase'"]
    positions = [text.find(s) for s in ADR_SECTIONS]
    if -1 in positions or positions != sorted(positions):
        problems.append(f"sections must appear in order: {ADR_SECTIONS}")
    status = re.search(r"## Status\s+(\w+)", text)
    if not status or status.group(1) not in ADR_STATUSES:
        problems.append(f"status must start with one of {ADR_STATUSES}")
    return problems


def check_mermaid(text):
    first = text.strip().splitlines()[0].strip()
    problems = [] if first in ("C4Context", "C4Container") else [f"unexpected diagram type {first!r}"]
    ids = set(MERMAID_ELEMENT.findall(text))
    problems += [f"Rel uses undefined id {i!r}" for pair in MERMAID_REL.findall(text) for i in pair if i not in ids]
    return problems + ([] if balanced(text) else ["unbalanced brackets"])


def check_dsl(text):
    ids = {name for name, _ in DSL_ELEMENT.findall(text)}
    systems = {name for name, kind in DSL_ELEMENT.findall(text) if kind == "softwareSystem"}
    problems = [f"relationship uses undefined id {i!r}" for pair in DSL_REL.findall(text) for i in pair if i not in ids]
    problems += [f"view scope {s!r} is not a softwareSystem" for s in DSL_VIEW.findall(text) if s not in systems]
    return problems + ([] if balanced(text, ("{}",)) else ["unbalanced braces"])


CHECKS = {"adr-*.md": check_adr, "*.mmd": check_mermaid, "*.dsl": check_dsl}


def main(folder=DOCS):
    failures = 0
    for pattern, checker in CHECKS.items():
        for path in sorted(folder.glob(pattern)):
            problems = checker(path.read_text(encoding="utf-8"))
            failures += len(problems)
            print(f"{'OK  ' if not problems else 'FAIL'} {path.name}" + "".join(f"\n     - {p}" for p in problems))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
