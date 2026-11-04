"""Agent assist (lesson 6): a LOCAL model drafts ADR 2 from Nygard's template; code decides if it is usable.

Safety boundary: the agent only proposes text. check_docs.check_adr + the rules below accept or reject it,
nothing is written to doc/arch/, and the lesson 3 boundary checker stays the authority on the code.
Run:  python agent_assist.py          (deterministic fake model, no download)
      python agent_assist.py --real   (Ollama/llama.cpp at LOCAL_MODEL_URL, default http://localhost:11434/v1)
"""
import argparse
import pathlib
import re
import subprocess
import sys

from check_docs import DOCS, check_adr

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent (vendored helper)
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

BOUNDARY_LAB = HERE.parent / "03-modular-monolith"
BRIEF = {
    "Title": "Modules talk only through public interfaces",
    "Context": "Library Loans is one deployable with two modules, catalog and loans. loans started to reach "
               "into catalog's internal store, so a storage change in catalog broke loans.",
    "Decision": "We will let a module import only another module's package (its __init__), never its internal/ "
                "package. check_boundaries.py enforces this in CI and fails the build on a violation.",
    "Consequences": "Modules can change their internals freely and could later be split out. New cross-module "
                    "needs require a public function first, which adds a small amount of code.",
}
MUST_MENTION = ["check_boundaries.py"]  # a decision without its automated check is only a wish
SYSTEM = "You draft architecture documents for review. You only propose; a human accepts or rejects."


def next_adr_number(folder=DOCS):
    numbers = [int(m.group(1)) for p in folder.glob("adr-*.md") if (m := re.match(r"adr-(\d+)", p.name))]
    return max(numbers, default=0) + 1


def build_prompt(number, brief=BRIEF, problems=()):
    lines = ["[[ADR-DRAFT]] Write an Architecture Decision Record in Michael Nygard's format.",
             f"Headings, in this order: '# ADR {number}: <short noun phrase>', '## Context', '## Decision',",
             "'## Status', '## Consequences'. Status must be 'Proposed.' because a human accepts ADRs.",
             "Reply with the Markdown only."]
    if problems:  # check -> retry: feed the checker's findings back, never the other way round
        lines.append("Problems: " + "; ".join(problems) + ". Fix them and return the full ADR again.")
    fields = "\n".join(f"{k}: {v}" for k, v in {"Number": number, **brief}.items())
    return "\n".join(lines) + f"\n<brief>\n{fields}\n</brief>"


def validate_draft(text, number, must_mention=MUST_MENTION):
    """Deterministic judge of the agent's output. Returns a list of problems ([] = usable draft)."""
    problems = check_adr(text)  # same Nygard checker the human-written ADRs pass
    title = re.match(r"# ADR (\d+):", text)
    if not title or int(title.group(1)) != number:
        problems.append(f"title must use the next free number {number}")
    status = re.search(r"## Status\s+(\w+)", text)
    if status and status.group(1) != "Proposed":
        problems.append(f"agent drafts must have status 'Proposed' (a human accepts ADRs), got '{status.group(1)}'")
    decision = re.search(r"## Decision\s+(.*?)(?=\n## |\Z)", text, re.S)
    for name in must_mention:
        if not decision or name not in decision.group(1):
            problems.append(f"Decision must name its automated check {name}")
    return problems


def draft_adr(base_url, model, number, attempts=2):
    """Ask, check, retry once with the checker's findings. Returns (draft, problems, log lines)."""
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": build_prompt(number)}]
    log, draft, problems = [], "", ["no attempt"]
    for attempt in range(1, attempts + 1):
        draft = chat(messages, base_url=base_url, model=model).strip()
        problems = validate_draft(draft, number)
        log.append(f"attempt {attempt}: " + ("OK" if not problems else "REJECTED")
                   + "".join(f"\n  - {p}" for p in problems))
        if not problems:
            break
        messages += [{"role": "assistant", "content": draft},
                     {"role": "user", "content": build_prompt(number, problems=problems)}]
    return draft, problems, log


def boundary_check():
    """The authoritative answer about the code comes from the fitness function, not from any ADR text."""
    run = subprocess.run([sys.executable, "check_boundaries.py"], cwd=BOUNDARY_LAB,
                         capture_output=True, text=True, encoding="utf-8")
    return run.returncode, run.stdout.strip().splitlines()[-1]


def main(argv=None):
    args = _parse(argv)
    server = None
    if args.real:
        base_url, model, label = None, None, "local model (LOCAL_MODEL_URL / LOCAL_MODEL)"
    else:
        server, base_url = fake_model_server.start_in_thread()
        model, label = "fake-model", "fake model server (deterministic stand-in, not a language model)"
    try:
        number = next_adr_number()
        print(f"model: {label}")
        print(f"next ADR number from doc/arch/: {number}")
        draft, problems, log = draft_adr(base_url, model, number)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("\n".join(log))
    if problems:
        print("draft rejected: nothing to review")
        return 1
    print("--- draft (proposal only: a human reviews it, saves it under doc/arch/ and sets Accepted) ---")
    print(draft)
    print("---")
    code, summary = boundary_check()
    print(f"fitness function (authoritative): {summary} (exit {code})")
    return 0


def _parse(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--real", action="store_true", help="use a real local model instead of the fake server")
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
