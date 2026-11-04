"""Checks content/explain/NN.md (EXPLAIN-SPEC.md). Run from anywhere: python research/explain_checks.py
Prints OK and exits 0 when every file passes; otherwise lists the problems and exits 1."""
import json, re, sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
EXPLAIN, RUNLOG = TOPIC / "content" / "explain", TOPIC / "research" / "explain_runs.md"
RANGES = {"L100": (350, 500), "Setup": (350, 500), "L200": (500, 700), "L300": (650, 850),
          "L400": (750, 1000), "Capstone": (600, 800), "L500": (900, 1300)}
APPLIED = ["## The intuition", "Where the analogy breaks:", "The one thing to remember:",
           "## Walkthrough: what actually happens when you run it"]
COMMON = ["## Common confusions", "## Check your understanding"]
NUM = re.compile(r"\d+(?:\.\d+)?")


def lessons():
    for level in ("L100", "L200", "L300", "L400", "L500"):
        yield from json.loads((TOPIC / "content" / f"{level}.json").read_text(encoding="utf-8"))


NEXT_STEP = re.compile(r"\n\s*\d+\. \*\*")


def blocks(text, start, stops):
    """Yield the text after each `start` marker up to the first stop marker, next numbered step or heading."""
    for m in re.finditer(re.escape(start), text):
        rest = text[m.end():]
        ends = [i for s in stops if (i := rest.find(s)) >= 0]
        if step := NEXT_STEP.search(rest):
            ends.append(step.start())
        yield rest[:min(ends)] if ends else rest


def fenced(text):
    return re.findall(r"```[^\n]*\n(.*?)```", text, re.S)


def check(lesson, log_numbers):
    n, level, title = lesson["number"], lesson["level"], lesson["title"]
    path, errs = EXPLAIN / f"{n:02d}.md", []
    if not path.exists():
        return [f"{path.name}: missing"]
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    lo, hi = RANGES[level]
    if not lo <= words <= hi:
        errs.append(f"{words} words, want {lo}-{hi} ({level})")
    if not text.startswith(f"# {title} — explained\n"):
        errs.append("first line must be '# <exact lesson title> — explained'")
    required = list(COMMON)
    if level == "L500":
        required.append("## The big picture")
        for th in lesson.get("theorems", []):
            required += [f"### {th['name']}", "**In plain words**", "**Why it is true (intuition)**",
                         "**See it in numbers**", "**Where it shows up in practice**"]
        if lesson.get("theorems"):
            required.append("## Worked problems")
        if "caseStudy" in lesson:
            required += ["## Worked analysis", "## A contrasting view"]
        if "readings" in lesson:
            required.append("## Reading guide")
    else:
        required += APPLIED
        if level == "L300":
            required.append("### Failure lab")
        if level in ("L400", "Capstone"):
            required.append("### The decision")
    errs += [f"missing '{h}'" for h in required if h not in text]
    # every number shown as observed output must appear in the recorded run log
    stops = ["**What it means", "\n## ", "\n### "]
    seen = list(blocks(text, "**What you see", stops))
    seen += ["\n".join(fenced(b)) for b in blocks(text, "**See it in numbers**", ["**Where it shows up"])]
    if level != "L500" and not seen:
        errs.append("no 'What you see' block")
    for block in seen:
        if block.lstrip(":* ").startswith("Expected (not run here)"):
            continue
        missing = sorted({x for x in NUM.findall(block) if x not in log_numbers}, key=len)
        if missing:
            errs.append(f"numbers not in run log: {missing[:8]}")
    opened, closed = text.count("<details>"), text.count("</details>")
    if opened != closed or text.count("<summary>") != text.count("</summary>"):
        errs.append(f"unbalanced <details>: {opened} open, {closed} close")
    check_part = text.split("## Check your understanding", 1)[-1]
    if check_part.count("<details>") < 3:
        errs.append("Check your understanding needs 3 <details> answers")
    confusions = text.split("## Common confusions", 1)[-1].split("## Check your understanding")[0]
    if confusions.count("**Q:**") != 3 or confusions.count("**A:**") != 3:
        errs.append("Common confusions needs exactly 3 Q/A entries")
    return [f"{path.name}: {e}" for e in errs]


def main():
    if not RUNLOG.exists():
        print(f"missing {RUNLOG}"); return 1
    log_numbers = set(NUM.findall(RUNLOG.read_text(encoding="utf-8")))
    all_lessons = list(lessons())
    problems = [p for lesson in all_lessons for p in check(lesson, log_numbers)]
    counts = {}
    for lesson in all_lessons:
        f = EXPLAIN / f"{lesson['number']:02d}.md"
        if f.exists():
            key = "L100" if lesson["level"] == "Setup" else lesson["level"]
            counts.setdefault(key, []).append(len(f.read_text(encoding="utf-8").split()))
    for level, ws in counts.items():
        print(f"{level}: {len(ws)} files, {min(ws)}-{max(ws)} words")
    if len(all_lessons) != 27:
        problems.append(f"expected 27 lessons, found {len(all_lessons)}")
    if problems:
        print("\n".join(problems)); return 1
    print("OK"); return 0


if __name__ == "__main__":
    sys.exit(main())
