"""Check content/explain/01.md … 27.md against kb/EXPLAIN-SPEC.md.

Run:  python research/explain_checks.py      (stdlib only; prints OK and exits 0 when every check passes)
Per file: exists; word count (whitespace tokens, like `wc -w`) within the level's range; exact title line; required
headings and markers for its level; 3 common confusions; 3 check questions with balanced <details>/<summary> blocks;
and every number quoted as real output (a "What you see" segment, or any fenced output block inside a walkthrough,
failure-lab, decision, theorem or reading section) appears in research/explain_runs.md.
"""
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
EXPLAIN = TOPIC / "content" / "explain"
RUNS = TOPIC / "research" / "explain_runs.md"
RANGES = {"L100": (350, 500), "L200": (500, 700), "L300": (650, 850), "L400": (750, 1000),
          "capstone": (600, 800), "L500": (900, 1300)}
NUM = re.compile(r"\d+(?:\.\d+)?(?:e-?\d+)?")
FENCE = re.compile(r"```([a-z]*)\n(.*?)```", re.S)


def lessons():
    out = {}
    for level in ("L100", "L200", "L300", "L400", "L500"):
        for lesson in json.loads((TOPIC / "content" / f"{level}.json").read_text(encoding="utf-8")):
            out[lesson["number"]] = lesson
    return out


def band(n):
    if n == 22:
        return "capstone"
    return "L100" if n <= 6 else "L200" if n <= 11 else "L300" if n <= 16 else "L400" if n <= 21 else "L500"


def section(text, start, stops=("\n## ",)):
    i = text.find(start)
    if i < 0:
        return ""
    j = min([k for k in (text.find(s, i + len(start)) for s in stops) if k > 0] or [len(text)])
    return text[i:j]


def quoted_output(text, n):
    """Text whose numbers must come from the run log."""
    parts = []
    for m in re.finditer(r"\*\*What you see[^*]*\*\*(.*?)(?=\*\*What it means|\n\d+\. \*\*|\n## |\Z)", text, re.S):
        parts.append(m.group(1))
    start = "\n## The big picture" if n >= 23 else "\n## Walkthrough"
    body = text[text.find(start):text.find("\n## Common confusions")] if start in text else ""
    body = body.split("\n## Worked problems")[0]
    parts += [code for lang, code in FENCE.findall(body) if lang != "mermaid"]
    return "\n".join(parts)


def check_file(n, lesson, log_numbers):
    errors = []
    path = EXPLAIN / f"{n:02d}.md"
    if not path.exists():
        return [f"{path.name}: missing"]
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    lo, hi = RANGES[band(n)]
    if not lo <= words <= hi:
        errors.append(f"{path.name}: {words} words, expected {lo}-{hi} ({band(n)})")
    if text.splitlines()[0] != f"# {lesson['title']} — explained":
        errors.append(f"{path.name}: first line must be '# {lesson['title']} — explained'")

    common = ["## Common confusions", "## Check your understanding"]
    if n <= 22:
        need = ["## The intuition", "**Analogy:**", "Where the analogy breaks:", "The one thing to remember:",
                "## Walkthrough: what actually happens when you run it", "**You run**", "**What happens inside:**",
                "**What you see", "**What it means"] + common
        if 12 <= n <= 16:
            need += ["## Failure lab", "**Inject:**", "**Symptom:**", "**Diagnose:**", "**Fix:**", "**Proof:**"]
        if 17 <= n <= 21:
            need += ["## Failure lab", "## Walkthrough: the decision", "ADR", "fitness function"]
        if n == 22:
            need += ["## Walkthrough: the decisions", "ADR"]
        intuition = section(text, "## The intuition")
        if not FENCE.search(intuition):
            errors.append(f"{path.name}: the intuition needs one diagram (``` or ```mermaid block)")
    else:
        need = ["## The big picture", "## Worked problems", "*Why:*"] + common
        for t in lesson.get("theorems", []):
            need.append(f"### {t['name']}")
        if lesson.get("theorems"):
            k = len(lesson["theorems"])
            for marker in ("**In plain words:**", "**Why it is true (intuition):**", "**See it in numbers:**",
                           "**Where it shows up in practice:**"):
                if text.count(marker) != k:
                    errors.append(f"{path.name}: '{marker}' appears {text.count(marker)}x, expected {k}")
        if n == 26:
            need += ["## Worked analysis", "## A contrasting view", "ACM"]
        if n == 27:
            need += ["## Reading guide: Grover", "## Reading guide: Preskill"]
            for marker in ("**Read first:**", "**Skim or skip", "**Three ideas to take away:**", "**How it connects to the labs:**"):
                if text.count(marker) != 2:
                    errors.append(f"{path.name}: '{marker}' should appear once per paper")
    errors += [f"{path.name}: missing '{h}'" for h in need if h not in text]

    confusions = section(text, "## Common confusions")
    if len(re.findall(r"(?m)^- \*\*Q:\*\*.*\*\*A:\*\*", confusions)) != 3:
        errors.append(f"{path.name}: need exactly 3 '- **Q:** … **A:** …' confusions")
    quiz = section(text, "## Check your understanding")
    if len(re.findall(r"(?m)^\d+\. ", quiz)) != 3:
        errors.append(f"{path.name}: need exactly 3 numbered questions")
    for open_tag, close_tag in (("<details>", "</details>"), ("<summary>", "</summary>")):
        if text.count(open_tag) != text.count(close_tag):
            errors.append(f"{path.name}: unbalanced {open_tag}")
    if quiz.count("<details><summary>Answer</summary>") != 3:
        errors.append(f"{path.name}: need 3 '<details><summary>Answer</summary>' answers")

    missing = sorted({x for x in NUM.findall(quoted_output(text, n)) if x not in log_numbers}, key=float)
    if missing:
        errors.append(f"{path.name}: quoted numbers not in explain_runs.md: {missing}")
    return errors, words


def main():
    if not RUNS.exists():
        sys.exit("research/explain_runs.md missing")
    log = RUNS.read_text(encoding="utf-8")
    if not re.search(r"Run: 20\d\d-\d\d-\d\d", log):
        sys.exit("explain_runs.md: no dated runs")
    log_numbers = set(NUM.findall(log))
    errors, counts = [], {}
    for n, lesson in sorted(lessons().items()):
        result = check_file(n, lesson, log_numbers)
        if isinstance(result, list):
            errors += result
            continue
        errs, words = result
        errors += errs
        counts.setdefault(band(n), []).append(words)
    for name, values in counts.items():
        print(f"{name:8s} {len(values)} files, {min(values)}-{max(values)} words")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
