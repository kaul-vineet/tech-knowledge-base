"""Checks for content/explain/NN.md (EXPLAIN-SPEC.md). Run from the astronomy folder or anywhere:

python research/explain_checks.py      -> prints OK and exits 0, or lists every problem and exits 1
"""
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
EXPLAIN = TOPIC / "content" / "explain"
RUNLOG = TOPIC / "research" / "explain_runs.md"
LEVELS = {"L100": range(1, 7), "L200": range(7, 12), "L300": range(12, 17), "L400": range(17, 22),
          "Capstone": [22], "L500": range(23, 28)}
WORDS = {"L100": (350, 500), "L200": (500, 700), "L300": (650, 850), "L400": (750, 1000),
         "Capstone": (600, 800), "L500": (900, 1300)}
NUMBER = re.compile(r"\d+(?:\.\d+)?(?:e[+-]?\d+)?")


def level_of(n):
    return next(k for k, v in LEVELS.items() if n in v)


def titles():
    out = {}
    for name in ("L100", "L200", "L300", "L400", "L500"):
        for lesson in json.loads((TOPIC / "content" / f"{name}.json").read_text(encoding="utf-8")):
            out[lesson["number"]] = lesson["title"]
    return out


def blocks(text, start, ends):
    """Text after each `start` marker up to the next marker in `ends` (or the next heading)."""
    out = []
    for m in re.finditer(re.escape(start), text):
        rest = text[m.end():]
        cut = [rest.find(e) for e in ends if rest.find(e) >= 0]
        nxt = re.search(r"^#{2,3} ", rest, re.M)
        if nxt:
            cut.append(nxt.start())
        out.append(rest[:min(cut)] if cut else rest)
    return out


def numbers_missing(block, log):
    if block.strip().startswith("Expected (not run here)"):
        return []  # documented expectation for an SDK/service not available here (never quoted as a run)
    return [n for n in NUMBER.findall(block) if n not in log]


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    if not m:
        return ""
    nxt = re.search(r"^## ", text[m.end():], re.M)
    return text[m.end():m.end() + nxt.start()] if nxt else text[m.end():]


def check_file(n, title, log):
    p = EXPLAIN / f"{n:02d}.md"
    if not p.exists():
        return [f"{p.name}: missing"]
    text = p.read_text(encoding="utf-8")
    lvl, errs = level_of(n), []
    words = len(text.split())
    lo, hi = WORDS[lvl]
    if not lo <= words <= hi:
        errs.append(f"{p.name}: {words} words, {lvl} needs {lo}-{hi}")
    if text.splitlines()[0] != f"# {title} — explained":
        errs.append(f"{p.name}: first line must be '# {title} — explained'")
    common = ["## Common confusions", "## Check your understanding"]
    if lvl == "L500":
        need = ["## The big picture"] + common
        if n in (23, 24, 25):
            need += ["## Worked problems", "**In plain words**", "**Why it is true (intuition)**",
                     "**See it in numbers**", "**Where it shows up in practice**"]
        if n == 26:
            need += ["## Worked analysis", "## A contrasting view"]
        if n == 27:
            need += ["## Reading guide"]
    else:
        need = ["## The intuition", "## Walkthrough: what actually happens when you run it", "Where the analogy breaks:",
                "The one thing to remember:", "**You run**", "**What happens inside**", "**What you see**",
                "**What it means / what would look wrong**"] + common
        if lvl == "L300":
            need += ["Failure lab"] + [f"— {w}" for w in ("inject", "diagnose", "fix", "proof")]
        if lvl in ("L400", "Capstone"):
            need += ["Failure lab", "### The decision", "fitness"]
        intuition = section(text, "The intuition")
        if "```" not in intuition:
            errs.append(f"{p.name}: no diagram (``` block) in The intuition")
        counts = {k: text.count(k) for k in ("**You run**", "**What happens inside**", "**What you see**",
                                             "**What it means / what would look wrong**")}
        if len(set(counts.values())) != 1:
            errs.append(f"{p.name}: walkthrough markers unbalanced {counts}")
    errs += [f"{p.name}: missing '{h}'" for h in need if h not in text]
    confusions = section(text, "Common confusions")
    if confusions.count("**Q:**") != 3 or confusions.count("**A:**") != 3:
        errs.append(f"{p.name}: Common confusions needs exactly 3 Q/A entries")
    check = section(text, "Check your understanding")
    if not (check.count("<details>") == check.count("</details>") == check.count("<summary>Answer</summary>") == 3):
        errs.append(f"{p.name}: Check your understanding needs 3 balanced <details> answers")
    if text.count("<details>") != text.count("</details>"):
        errs.append(f"{p.name}: unbalanced <details> blocks")
    quoted = blocks(text, "**What you see**", ["**What it means"]) + blocks(text, "**See it in numbers**", ["**Where it shows up"])
    for b in quoted:
        missing = numbers_missing(b, log)
        if missing:
            errs.append(f"{p.name}: numbers not in the run log: {sorted(set(missing))[:8]}")
    return errs


def main():
    if not RUNLOG.exists():
        print("FAIL: research/explain_runs.md missing")
        return 1
    log = RUNLOG.read_text(encoding="utf-8")
    t = titles()
    errs = [e for n in range(1, 28) for e in check_file(n, t[n], log)]
    for lvl, ns in LEVELS.items():
        counts = [len((EXPLAIN / f"{n:02d}.md").read_text(encoding="utf-8").split())
                  for n in ns if (EXPLAIN / f"{n:02d}.md").exists()]
        if counts:
            print(f"{lvl:<8} words {min(counts)}-{max(counts)} (allowed {WORDS[lvl][0]}-{WORDS[lvl][1]})")
    if errs:
        print("\n".join(errs))
        print(f"FAIL: {len(errs)} problem(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
