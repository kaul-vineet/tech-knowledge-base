"""Checks for content/explain/NN.md (EXPLAIN-SPEC.md). Run: python research/explain_checks.py  -> prints OK, exit 0."""
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
EXPLAIN = TOPIC / "content" / "explain"
RUN_LOG = TOPIC / "research" / "explain_runs.md"
NUM = re.compile(r"\d+(?:\.\d+)?")
FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
RANGES = {"L100": (350, 500), "L200": (500, 700), "L300": (650, 850), "L400": (750, 1000),
          "capstone": (600, 800), "L500": (900, 1300)}
LAB_HEADINGS = ["## The intuition", "## Walkthrough: what actually happens when you run it",
                "## Common confusions", "## Check your understanding", "Where the analogy breaks:",
                "The one thing to remember:", "**You run**", "**What you see"]
L500_HEADINGS = ["## The big picture", "## Common confusions", "## Check your understanding"]


def band(n):
    if n == 22:
        return "capstone"
    return "L100" if n <= 6 else "L200" if n <= 11 else "L300" if n <= 16 else "L400" if n <= 21 else "L500"


def lessons():
    out = {}
    for level in ("L100", "L200", "L300", "L400", "L500"):
        for lesson in json.loads((TOPIC / "content" / f"{level}.json").read_text(encoding="utf-8")):
            out[lesson["number"]] = lesson
    return out


def quoted_numbers(text):
    """Numbers in fenced blocks outside the intuition section, plus `code` spans on 'What you see' lines."""
    found = []
    for section in re.split(r"\n(?=## )", text):
        if section.startswith("## The intuition"):
            continue
        for block in FENCE.findall(section):
            found += NUM.findall(block)
        for line in section.splitlines():
            if "**What you see" in line:
                for span in re.findall(r"`([^`]+)`", line.split("**What you see", 1)[1]):
                    found += NUM.findall(span)
    return found


def check_file(n, lesson, log_numbers):
    errors, path = [], EXPLAIN / f"{n:02d}.md"
    if not path.exists():
        return [f"{path.name}: missing"]
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    lo, hi = RANGES[band(n)]
    if not lo <= words <= hi:
        errors.append(f"{path.name}: {words} words, expected {lo}-{hi} ({band(n)})")
    if text.splitlines()[0] != f"# {lesson['title']} — explained":
        errors.append(f"{path.name}: first line is not '# {lesson['title']} — explained'")
    required = list(L500_HEADINGS if n >= 23 else LAB_HEADINGS)
    if 12 <= n <= 16:
        required.append("Failure lab")
    if 17 <= n <= 21:
        required.append("## The decision")
    if n == 22:
        required.append("## The decisions")
    if 23 <= n <= 25:
        required += ["## Worked problems", "**In plain words.**", "**Why it is true", "**See it in numbers",
                     "**Where it shows up"]
        required += [f"### {t['name'].split(' - ')[0]}" for t in lesson.get("theorems", [])]
    if n == 26:
        required += ["framework", "## A contrasting view"]
    if n == 27:
        required += ["## Paper 1", "## Paper 2", "**Read first.**", "**Skim or skip", "**Three ideas"]
    errors += [f"{path.name}: missing '{h}'" for h in required if h not in text]
    if n <= 22:
        intuition = text.split("## The intuition", 1)[-1].split("\n## ", 1)[0]
        if "```" not in intuition:
            errors.append(f"{path.name}: no diagram in The intuition")
    if len(re.findall(r"^\*\*Q:\*\*", text, re.M)) != 3:
        errors.append(f"{path.name}: expected 3 common-confusion entries")
    opens, closes = text.count("<details>"), text.count("</details>")
    summaries = text.count("<summary>Answer</summary>")
    if not opens == closes == summaries == 3:
        errors.append(f"{path.name}: details/summary unbalanced or not 3 ({opens}/{closes}/{summaries})")
    if text.count("```") % 2:
        errors.append(f"{path.name}: unbalanced code fences")
    missing = sorted({x for x in quoted_numbers(text) if x not in log_numbers}, key=lambda s: (len(s), s))
    if missing:
        errors.append(f"{path.name}: quoted numbers not in run log: {missing[:12]}")
    return errors, words


def main():
    if not RUN_LOG.exists():
        print("FAIL: research/explain_runs.md missing")
        return 1
    log_numbers = set(NUM.findall(RUN_LOG.read_text(encoding="utf-8")))
    info, errors, per_band = lessons(), [], {}
    for n in range(1, 28):
        result = check_file(n, info[n], log_numbers)
        if isinstance(result, list):
            errors += result
            continue
        errs, words = result
        errors += errs
        per_band.setdefault(band(n), []).append(words)
    for b, ws in per_band.items():
        print(f"{b:8} {len(ws)} files, {min(ws)}-{max(ws)} words")
    if errors:
        print("\n".join(errors))
        print(f"FAIL ({len(errors)} problems)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
