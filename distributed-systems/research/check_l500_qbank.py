"""Validate content/qbank/L500.json and content/assessment/concept-inventory.json with the rules of
tools/check_qbank.py (which only reads L100-L400). python research/check_l500_qbank.py -> exit 1 on any error.

Rules applied (QBANK-SPEC + L500-SPEC): >= 40 questions, every L500 lesson >= 6, required fields, level L500,
lesson exists in content/L500.json, known type, difficulty 1-3, exactly 4 distinct options, answer index 0-3,
no 'all/none of the above', explanation >= 30 chars, no duplicate ids or questions (across the L500 bank, the
inventory and L100-L400), each answer position 15-35% (spec target 20-30%), warning if the correct option is
the longest in more than 45%. Concept inventory: exactly 15 items, level L500, lesson 23.
"""
import collections
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)
FIELDS = ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source")


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def load(rel):
    return json.loads((TOPIC / rel).read_text(encoding="utf-8"))


def check_items(name, qs, lessons, seen_q, ids, errs, warns, min_n):
    pos, types, per_lesson = collections.Counter(), collections.Counter(), collections.Counter()
    if len(qs) < min_n:
        errs.append(f"{name}: {len(qs)} items (< {min_n})")
    for q in qs:
        qid = q.get("id", "?")
        for k in FIELDS:
            if k not in q:
                errs.append(f"{qid}: missing {k}")
        if qid in ids:
            errs.append(f"duplicate id {qid}")
        ids.add(qid)
        if q.get("level") != "L500":
            errs.append(f"{qid}: level {q.get('level')} (want L500)")
        if q.get("lesson") not in lessons:
            errs.append(f"{qid}: lesson {q.get('lesson')} not in content/L500.json")
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
        key = norm(q.get("question", "") + " " + q.get("code", ""))
        if key in seen_q:
            errs.append(f"{qid}: duplicate of {seen_q[key]}")
        seen_q[key] = qid
        pos[q.get("answer")] += 1
        types[q.get("type")] += 1
        per_lesson[q.get("lesson")] += 1
    n = len(qs)
    for a in range(4):
        share = pos[a] / n if n else 0
        if not 0.15 <= share <= 0.35:
            errs.append(f"{name}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30%)")
    longest = sum(1 for q in qs if len(q["options"]) == 4 and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    if n and longest / n > 0.45:
        warns.append(f"{name}: correct option is the longest in {longest / n:.0%}")
    print(f"  {name}: {n} items · types {dict(types)} · answers "
          f"{dict(sorted(('ABCD'[k], v) for k, v in pos.items() if isinstance(k, int) and 0 <= k < 4))} · "
          f"correct=longest {longest}/{n}")
    return per_lesson


def main():
    errs, warns, ids, seen_q = [], [], set(), {}
    for lv in ("L100", "L200", "L300", "L400"):  # cross-level duplicate detection only
        p = TOPIC / "content" / "qbank" / f"{lv}.json"
        if p.exists():
            for q in json.loads(p.read_text(encoding="utf-8")):
                ids.add(q["id"])
                seen_q[norm(q["question"] + " " + q.get("code", ""))] = q["id"]
    lessons = {l["number"] for l in load("content/L500.json")}
    per_lesson = check_items("qbank/L500.json", load("content/qbank/L500.json"), lessons, seen_q, ids, errs, warns, 40)
    for num in sorted(lessons):
        if per_lesson[num] < 6:
            errs.append(f"lesson {num}: {per_lesson[num]} questions (< 6)")
    inv = load("content/assessment/concept-inventory.json")
    check_items("assessment/concept-inventory.json", inv, lessons, seen_q, ids, errs, warns, 15)
    if len(inv) != 15:
        errs.append(f"concept inventory: {len(inv)} items (spec: 15)")
    if any(q.get("lesson") != 23 for q in inv):
        errs.append("concept inventory: every item must have lesson 23")
    print(f"distributed-systems L500: per lesson {dict(sorted(per_lesson.items()))}")
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
