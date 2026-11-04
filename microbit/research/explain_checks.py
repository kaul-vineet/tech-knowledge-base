"""Checks for the "Explained" tab of the micro:bit topic (content/explain/01.md ... 27.md).

For every lesson file: it exists, the title line matches the lesson JSON, the word count is in the
EXPLAIN-SPEC range for its level, the required headings/labels are present, there are 3 common
confusions and 3 balanced <details> answers, and every number inside a "What you see" or
"See it in numbers" code block appears in the recorded run log (research/explain_runs.md).

Run from anywhere:  python3 research/explain_checks.py   -> prints OK and exits 0.
"""
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
EXPLAIN = TOPIC / "content" / "explain"
RUNLOG = TOPIC / "research" / "explain_runs.md"

RANGES = {"L100": (350, 500), "L200": (500, 700), "L300": (650, 850), "L400": (750, 1000),
          "capstone": (600, 800), "L500": (900, 1300)}

INTUITION = ["## The intuition", "Where the analogy breaks:", "The one thing to remember:",
             "## Walkthrough: what actually happens when you run it", "**You run**", "**What you see**",
             "## Common confusions", "## Check your understanding"]
L500_COMMON = ["## The big picture", "## Worked problems", "## Common confusions", "## Check your understanding"]
THEOREM_LABELS = ["**In plain words**", "**Why it is true (intuition)**", "**See it in numbers**",
                  "**Where it shows up in practice**"]
NUMBER = re.compile(r"(?<![\d.])\.\d+|\d+(?:\.\d+)?(?:e-?\d+)?")
OUTPUT_LABEL = re.compile(r"\*\*(What you see|See it in numbers)\*\*")
FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)


def lessons():
    out = {}
    for level in ("L100", "L200", "L300", "L400", "L500"):
        for les in json.loads((TOPIC / "content" / (level + ".json")).read_text(encoding="utf-8")):
            out[les["number"]] = les
    return out


def band(num):
    if num <= 6:
        return "L100"
    if num <= 11:
        return "L200"
    if num <= 16:
        return "L300"
    if num <= 21:
        return "L400"
    if num == 22:
        return "capstone"
    return "L500"


def output_blocks(text):
    """Code blocks that follow a 'What you see' / 'See it in numbers' label, up to the next bold label or heading."""
    blocks = []
    for m in OUTPUT_LABEL.finditer(text):
        rest = text[m.end():]
        stop = re.search(r"\*\*(What it means|You run|What happens inside|Where it shows up)|^#{1,3} |^\d+\. \*\*",
                         rest, re.M)
        segment = rest[:stop.start()] if stop else rest
        blocks += FENCE.findall(segment)
    return blocks


def in_log(token, log):
    # not glued to a longer number on either side ("75" must not match inside "0.75" or "750")
    return re.search(r"(?<!\d)(?<!\d\.)" + re.escape(token) + r"(?!\d)(?!\.\d)", log) is not None


def check(num, les, log, report):
    errors = []
    path = EXPLAIN / ("%02d.md" % num)
    if not path.exists():
        return ["%02d.md missing" % num]
    text = path.read_text(encoding="utf-8")
    title = "# %s — explained" % les["title"]
    if text.splitlines()[0].strip() != title:
        errors.append("title line must be %r" % title)
    words = len(text.split())   # every whitespace-separated token, = wc -w in a UTF-8 locale (the stricter count)
    level = band(num)
    lo, hi = RANGES[level]
    report.setdefault(level, []).append(words)
    if not lo <= words <= hi:
        errors.append("%d words, %s range is %d-%d" % (words, level, lo, hi))

    if num <= 22:
        required = list(INTUITION)
        if not re.search(r"## The intuition.*?```", text, re.S):
            errors.append("intuition needs a diagram in a ``` block")
        if 12 <= num <= 16:
            required += ["### Failure lab: inject → symptom → diagnose → fix → proof"]
        if num >= 17:
            required += ["ADR", "fitness"]
    else:
        required = list(L500_COMMON)
        if num <= 25:
            for th in les["theorems"]:
                head = "### " + th["name"]
                if head not in text:
                    errors.append("missing theorem heading %r" % head)
                    continue
                section = text.split(head, 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
                for label in THEOREM_LABELS:
                    if label not in section:
                        errors.append("%s: missing %s" % (th["name"], label))
                if not re.search(r"^\d\. ", section, re.M):
                    errors.append("%s: proof skeleton needs numbered moves" % th["name"])
        elif num == 26:
            required += ["## Worked analysis", "framework", "## A contrasting view", "**See it in numbers**"]
        else:
            required += ["## Reading guide 1", "## Reading guide 2", "**Read first**", "**Skip on the first pass**",
                         "**Three ideas to take away**", "**See it in numbers**"]
    for r in required:
        if r not in text:
            errors.append("missing %r" % r)

    confusions = text.split("## Common confusions", 1)[-1].split("## Check your understanding", 1)[0]
    if confusions.count("**Q:**") != 3 or confusions.count("**A:**") != 3:
        errors.append("need exactly 3 Q/A common confusions")
    opened, closed = text.count("<details>"), text.count("</details>")
    summaries = text.count("<summary>Answer</summary>")
    checks = text.split("## Check your understanding", 1)[-1]
    if opened != closed or opened != summaries or checks.count("<details>") != 3 or opened != 3:
        errors.append("<details> unbalanced or not 3 (open %d, close %d, summary %d)" % (opened, closed, summaries))

    blocks = output_blocks(text)
    if not blocks:
        errors.append("no quoted output blocks found")
    for block in blocks:
        for token in NUMBER.findall(block):
            if not in_log(token, log):
                errors.append("number %s in a quoted output is not in research/explain_runs.md" % token)
    return errors


def main():
    log = RUNLOG.read_text(encoding="utf-8") if RUNLOG.exists() else ""
    if not log:
        print("FAIL research/explain_runs.md missing or empty")
        return 1
    info = lessons()
    report, failed = {}, []
    for num in range(1, 28):
        for e in check(num, info[num], log, report):
            failed.append("%02d.md: %s" % (num, e))
    for level in ("L100", "L200", "L300", "L400", "capstone", "L500"):
        w = report.get(level, [])
        if w:
            print("%-8s files %d, words %d-%d (range %d-%d)" % (level, len(w), min(w), max(w), *RANGES[level]))
    if failed:
        print("\n".join(failed))
        print("FAILED (%d problems)" % len(failed))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
