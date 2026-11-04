"""Checks content/explain/NN.md against EXPLAIN-SPEC.md.

For every lesson 1-27: the file exists, its word count (whitespace tokens, as wc -w) is in the level's range, the required
headings are present, every number quoted inside a "What you see" block (and, for L500, inside the code
blocks of "See it in numbers") appears in research/explain_runs.md, and <details> blocks are balanced.
python research/explain_checks.py    -> prints OK and exits 0
"""
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
EXPLAIN = TOPIC / "content" / "explain"
RUNS = TOPIC / "research" / "explain_runs.md"
RANGES = {"L100": (350, 500), "L200": (500, 700), "L300": (650, 850), "L400": (750, 1000),
          "capstone": (600, 800), "L500": (900, 1300)}
COMMON = ["## Common confusions", "## Check your understanding"]
APPLIED = ["## The intuition", "## Walkthrough: what actually happens when you run it",
           "Where the analogy breaks:", "The one thing to remember:", "**You run**",
           "**What happens inside", "**What you see", "**What it means"]
NUMBER = re.compile(r"(?<![\w.])-?\d+(?:[.,]\d+)*(?:e[+-]?\d+)?")


def lessons():
    out = {}
    for level in ("L100", "L200", "L300", "L400", "L500"):
        for lesson in json.loads((TOPIC / "content" / f"{level}.json").read_text(encoding="utf-8")):
            out[lesson["number"]] = (level, lesson)
    return out


def words(path):
    """Whitespace-separated tokens, like POSIX wc -w; never lower than wc -w here (box-drawing glyphs count too)."""
    return len(path.read_text(encoding="utf-8").split())


def band(n, level):
    return "capstone" if n == 22 else level


def see_blocks(text):
    """Text of every 'What you see' block: up to the next label, numbered step or heading."""
    blocks = []
    for m in re.finditer(r"\*\*What you see:?\*\*:?", text):
        rest = text[m.end():]
        stop = re.search(r"\*\*What it means|\*\*You run\*\*|\n\s*\d+\. \*\*|\n#", rest)
        blocks.append(rest[:stop.start()] if stop else rest)
    return blocks


def numbers_section_code(text):
    """Code blocks inside 'See it in numbers' sections (L500)."""
    blocks = []
    for m in re.finditer(r"\*\*See it in numbers\*\*", text):
        rest = text[m.end():]
        stop = re.search(r"\*\*Where it shows up in practice\*\*|\n#", rest)
        blocks += re.findall(r"```[^\n]*\n(.*?)```", rest[:stop.start()] if stop else rest, re.S)
    return blocks


def check_numbers(name, blocks, log, problems):
    for block in blocks:
        if block.strip().startswith("Expected (not run here)"):
            continue
        for num in NUMBER.findall(block):
            num = num.rstrip(".,")
            if num and num not in log:
                problems.append(f"{name}: quoted number {num!r} not found in explain_runs.md")


def main():
    problems, ranges = [], {}
    log = RUNS.read_text(encoding="utf-8") if RUNS.exists() else ""
    if not log:
        problems.append("research/explain_runs.md missing or empty")
    for n, (level, lesson) in sorted(lessons().items()):
        path = EXPLAIN / f"{n:02d}.md"
        if not path.exists():
            problems.append(f"{path.name}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        key = band(n, level)
        lo, hi = RANGES[key]
        w = words(path)
        ranges.setdefault(key, []).append(w)
        if not lo <= w <= hi:
            problems.append(f"{path.name}: {w} words, outside {lo}-{hi} for {key}")
        title = f"# {lesson['title']} — explained"
        if text.splitlines()[0].strip() != title:
            problems.append(f"{path.name}: first line must be {title!r}")
        required = list(COMMON)
        if level == "L500":
            required += ["## The big picture"]
            if n <= 25:
                required += ["## Worked problems", "**In plain words**", "**Why it is true (intuition)**",
                             "**See it in numbers**", "**Where it shows up in practice**"]
                required += [f"### {t['name']}" for t in lesson["theorems"]]
                if text.count("**See it in numbers**") < len(lesson["theorems"]):
                    problems.append(f"{path.name}: one 'See it in numbers' per theorem required")
            elif n == 26:
                required += ["## The case, analysed step by step", "## A contrasting view"]
            else:
                required += ["## Reading guide"] + [f"### {r['citation'].split(',')[0]}" for r in lesson["readings"]]
        else:
            required += APPLIED
            if level == "L300":
                required += ["## Failure lab"]
            if level == "L400":
                required += ["## The decision"]
        for h in required:
            if h not in text:
                problems.append(f"{path.name}: missing {h!r}")
        if text.count("**Q:**") != 3:
            problems.append(f"{path.name}: expected 3 '**Q:**' confusions, found {text.count('**Q:**')}")
        opened, closed = text.count("<details>"), text.count("</details>")
        if opened != closed or opened < 3:
            problems.append(f"{path.name}: <details> {opened} opened / {closed} closed (need >= 3, balanced)")
        check_numbers(path.name, see_blocks(text), log, problems)
        if level == "L500":
            check_numbers(path.name, numbers_section_code(text), log, problems)
    for p in problems:
        print("FAIL", p)
    for key in ("L100", "L200", "L300", "L400", "capstone", "L500"):
        if key in ranges:
            print(f"{key}: {min(ranges[key])}-{max(ranges[key])} words over {len(ranges[key])} files")
    if problems:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
