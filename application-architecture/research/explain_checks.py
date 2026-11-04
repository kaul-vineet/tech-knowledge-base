"""Checks for content/explain/NN.md (EXPLAIN-SPEC.md). Run: python research/explain_checks.py  (prints OK, exit 0).

For every lesson 1-27: the file exists, the title matches the lesson, the word count is in the level's range (len(text.split()), the same as
`wc -w` in a UTF-8 locale; `wc -w` in the C locale skips tokens without ASCII characters, e.g. a lone "—", and gives
smaller counts),
the required headings are present, there are 3 confusions and 3 <details> answers, <details>/<summary> tags balance,
and every number shown as observed output (What you see / See it in numbers / failure-lab and proof blocks, i.e.
inline "What you see" text, inline `code` quotes and fenced output blocks in the walkthrough part) appears in research/explain_runs.md.
"""
import json
import pathlib
import re
import sys

TOPIC = pathlib.Path(__file__).resolve().parent.parent
EXPLAIN = TOPIC / "content" / "explain"
RUN_LOG = TOPIC / "research" / "explain_runs.md"

RANGES = {"L100": (350, 500), "L200": (500, 700), "L300": (650, 850), "L400": (750, 1000),
          "capstone": (600, 800), "L500": (900, 1300)}
COMMON = ["## Common confusions", "## Check your understanding"]
LAB_HEADINGS = ["## The intuition", "Where the analogy breaks:", "The one thing to remember:",
                "## Walkthrough: what actually happens when you run it"] + COMMON
THEORY = ["**In plain words:**", "**Why it is true (intuition):**", "**See it in numbers:**",
          "**Where it shows up in practice:**"]
EXTRA = {
    "L300": ["## Failure lab", "**Inject:**", "**Symptom:**", "**Diagnose:**", "**Fix:**", "**Proof:**"],
    "L500-theory": ["## The big picture", "## Worked problems"] + COMMON,
    26: ["## The big picture", "## Worked analysis with the ACM Code of Ethics", "## A contrasting view",
         "## Worked problems"] + COMMON,
    27: ["## The big picture", "## Reading guide 1", "## Reading guide 2", "**Read first:**", "**Skim or skip",
         "**Three ideas to take away:**", "**How it connects to the labs:**", "## Worked problems"] + COMMON,
}
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def lessons():
    for level in ("L100", "L200", "L300", "L400", "L500"):
        for lesson in json.loads((TOPIC / "content" / f"{level}.json").read_text(encoding="utf-8")):
            yield lesson["number"], level, lesson["title"]


def bucket(number, level):
    return "capstone" if number == 22 else level


def required(number, level):
    if level == "L500":
        return EXTRA[number] if number in EXTRA else EXTRA["L500-theory"] + THEORY
    return LAB_HEADINGS + (EXTRA["L300"] if level == "L300" else [])


def observed_segments(text, level):
    """Text that claims to be real output: inline 'What you see' parts and fenced non-diagram blocks after the intuition."""
    body = text
    if level != "L500":
        body = text.split("## Walkthrough", 1)[1] if "## Walkthrough" in text else ""
    body = body.split("## Common confusions", 1)[0]
    segments = [block for lang, block in re.findall(r"```(\w*)\n(.*?)```", body, re.S) if lang != "mermaid"]
    no_fences = re.sub(r"```.*?```", "", body, flags=re.S)
    segments += re.findall(r"\*\*What you see\*\*(.*?)(?=\*\*What it means|\n\d+\. \*\*|\n## |\Z)", no_fences, re.S)
    segments += re.findall(r"`([^`\n]+)`", no_fences)  # inline quotes such as `Ran 9 tests in 10.359s`
    return segments


def check_file(number, level, title, log):
    path = EXPLAIN / f"{number:02d}.md"
    if not path.exists():
        return [f"{path.name}: missing"], None
    text = path.read_text(encoding="utf-8")
    problems = []
    if text.splitlines()[0].strip() != f"# {title} — explained":
        problems.append(f"{path.name}: first line must be '# {title} — explained'")
    words = len(text.split())
    low, high = RANGES[bucket(number, level)]
    if not low <= words <= high:
        problems.append(f"{path.name}: {words} words, want {low}-{high}")
    problems += [f"{path.name}: missing '{h}'" for h in required(number, level) if h not in text]
    confusions = re.findall(r"^\*\*Q:\*\*", text, re.M)
    if len(confusions) != 3:
        problems.append(f"{path.name}: {len(confusions)} confusions, want 3")
    opened, closed = text.count("<details>"), text.count("</details>")
    summaries = text.count("<summary>Answer</summary>")
    if not opened == closed == summaries == 3:
        problems.append(f"{path.name}: <details> {opened}/{closed}, summaries {summaries} (want 3 balanced)")
    for segment in observed_segments(text, level):
        for value in NUMBER.findall(segment):
            if value not in log:
                problems.append(f"{path.name}: number {value} shown as output is not in explain_runs.md")
    return problems, words


def main():
    log = RUN_LOG.read_text(encoding="utf-8")
    problems, counts = [], {}
    for number, level, title in lessons():
        found, words = check_file(number, level, title, log)
        problems += found
        if words is not None:
            counts.setdefault(bucket(number, level), []).append(words)
    for name, values in counts.items():
        print(f"{name:<9} {len(values)} files, {min(values)}-{max(values)} words (want {RANGES[name][0]}-{RANGES[name][1]})")
    for problem in problems:
        print("PROBLEM", problem)
    print("OK" if not problems else f"FAILED ({len(problems)} problems)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
