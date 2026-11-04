"""Validate content/qbank/L500.json (and content/assessment/concept-inventory.json) with the same rules as
kb/tools/check_qbank.py, which only reads L100-L400. Run: python research/check_l500_qbank.py  (exit 1 on any error)"""
import collections
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)
KEYS = ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source")


def norm(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def check_items(name, qs, lessons, errs, warns, min_total, min_per_lesson, strict_balance):
    ids, seen, pos, types, per_lesson = set(), {}, collections.Counter(), collections.Counter(), collections.Counter()
    if len(qs) < min_total:
        errs.append(f"{name}: {len(qs)} questions (<{min_total})")
    for q in qs:
        qid = q.get("id", "?")
        for k in KEYS:
            if k not in q:
                errs.append(f"{qid}: missing {k}")
        if qid in ids:
            errs.append(f"duplicate id {qid}")
        ids.add(qid)
        if q.get("level") != "L500":
            errs.append(f"{qid}: level {q.get('level')} (want L500)")
        if q.get("lesson") not in lessons:
            errs.append(f"{qid}: lesson {q.get('lesson')} not in L500")
        if q.get("type") not in TYPES:
            errs.append(f"{qid}: bad type {q.get('type')}")
        if q.get("difficulty") not in (1, 2, 3):
            errs.append(f"{qid}: bad difficulty")
        o = q.get("options", [])
        if len(o) != 4 or len(set(map(norm, o))) != 4:
            errs.append(f"{qid}: need 4 distinct options")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            errs.append(f"{qid}: bad answer index")
        if any(BANNED.search(x) for x in o):
            errs.append(f"{qid}: 'all/none of the above' not allowed")
        if len(q.get("explanation", "")) < 30:
            errs.append(f"{qid}: explanation too short")
        if q.get("code") and len(q["code"].splitlines()) > 15:
            errs.append(f"{qid}: code snippet longer than 15 lines")
        k = norm(q.get("question", "") + " " + q.get("code", ""))
        if k in seen:
            errs.append(f"{qid}: duplicate of {seen[k]}")
        seen[k] = qid
        pos[q.get("answer")] += 1
        types[q.get("type")] += 1
        per_lesson[q.get("lesson")] += 1
    n = len(qs)
    lo, hi = (0.20, 0.30) if strict_balance else (0.15, 0.35)
    for a in range(4):
        share = pos[a] / n if n else 0
        if not lo <= share <= hi:
            errs.append(f"{name}: answer {'ABCD'[a]} correct in {share:.0%} (want {lo:.0%}-{hi:.0%})")
    longest = sum(1 for q in qs if len(q["options"]) == 4 and
                  max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    if n and longest / n > 0.45:
        warns.append(f"{name}: correct option is the longest in {longest / n:.0%}")
    for num in lessons:
        if min_per_lesson and per_lesson[num] < min_per_lesson:
            errs.append(f"{name}: lesson {num} has {per_lesson[num]} questions (<{min_per_lesson})")
    print(f"  {name}: {n} questions · types {dict(types)} · answers "
          f"{dict(sorted(('ABCD'[k], v) for k, v in pos.items()))} · per lesson {dict(sorted(per_lesson.items()))} · "
          f"correct-is-longest {longest}/{n}")


def main() -> int:
    lessons = {l["number"] for l in json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))}
    errs, warns = [], []
    qb = json.loads((TOPIC / "content" / "qbank" / "L500.json").read_text(encoding="utf-8"))
    check_items("qbank/L500.json", qb, lessons, errs, warns, 40, 6, strict_balance=True)
    ci = json.loads((TOPIC / "content" / "assessment" / "concept-inventory.json").read_text(encoding="utf-8"))
    check_items("assessment/concept-inventory.json", ci, {23}, errs, warns, 15, 0, strict_balance=False)
    if len(ci) != 15 or any(q.get("lesson") != 23 for q in ci):
        errs.append("concept inventory must have exactly 15 items, all lesson 23")
    overlap = {norm(q["question"]) for q in qb} & {norm(q["question"]) for q in ci}
    if overlap:
        errs.append(f"concept inventory duplicates qbank questions: {len(overlap)}")
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    print("OK" if not errs else "FAILED")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
