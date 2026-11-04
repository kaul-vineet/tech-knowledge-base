"""Validate content/qbank/L500.json and content/assessment/concept-inventory.json with the rules of kb/tools/check_qbank.py.

Run:  python research/check_l500_qbank.py      (exit 1 on any error)
kb/tools/check_qbank.py only reads L100-L400, so this script applies the same rules (QBANK-SPEC.md) to L500:
>= 40 questions, >= 6 per lesson 23-27, required fields, valid type/difficulty, 4 distinct options, one answer index,
no 'all/none of the above', explanation >= 30 chars, no duplicates (also against L100-L400), answer positions 15-35%
(target 20-30%), and a warning if the correct option is the longest in > 45%. The concept inventory must have exactly
15 items, level L500, lesson 23, with the same per-item rules and position balance.
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


def check_items(name, qs, lessons, errs, warns, seen_q, ids):
    pos, types, per_lesson = collections.Counter(), collections.Counter(), collections.Counter()
    for q in qs:
        qid = q.get("id", "?")
        for k in FIELDS:
            if k not in q:
                errs.append(f"{qid}: missing {k}")
        if qid in ids:
            errs.append(f"duplicate id {qid}")
        ids.add(qid)
        if q.get("level") != "L500":
            errs.append(f"{qid}: level {q.get('level')}")
        if q.get("lesson") not in lessons:
            errs.append(f"{qid}: lesson {q.get('lesson')} not in {sorted(lessons)}")
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
        if "code" in q and len(q["code"].splitlines()) > 15:
            errs.append(f"{qid}: code snippet longer than 15 lines")
        k = norm(q.get("question", "") + " " + q.get("code", ""))
        if k in seen_q:
            errs.append(f"{qid}: duplicate of {seen_q[k]}")
        seen_q[k] = qid
        pos[q.get("answer")] += 1
        types[q.get("type")] += 1
        per_lesson[q.get("lesson")] += 1
    n = len(qs)
    for a in range(4):
        share = pos[a] / n if n else 0
        if not 0.15 <= share <= 0.35:
            errs.append(f"{name}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30%)")
    longest = sum(1 for q in qs if len(q["options"]) == 4
                  and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    if n and longest / n > 0.45:
        warns.append(f"{name}: correct option is the longest in {longest / n:.0%}")
    answers = {"ABCD"[k]: v for k, v in sorted(pos.items()) if isinstance(k, int) and 0 <= k < 4}
    print(f"  {name}: {n} questions · types {dict(types)} · answers {answers} · longest-correct {longest}/{n}")
    return per_lesson


def main():
    errs, warns, seen_q, ids = [], [], {}, set()
    for lv in ("L100", "L200", "L300", "L400"):                       # duplicates against earlier levels
        for q in load(f"content/qbank/{lv}.json"):
            seen_q[norm(q["question"] + " " + q.get("code", ""))] = q["id"]
            ids.add(q["id"])
    lessons = {l["number"] for l in load("content/L500.json")}
    if lessons != {23, 24, 25, 26, 27}:
        errs.append(f"content/L500.json lessons {sorted(lessons)}")
    bank = load("content/qbank/L500.json")
    if len(bank) < 40:
        errs.append(f"L500: {len(bank)} questions (<40)")
    per_lesson = check_items("L500", bank, lessons, errs, warns, seen_q, ids)
    for num in sorted(lessons):
        if per_lesson[num] < 6:
            errs.append(f"lesson {num}: {per_lesson[num]} questions (<6)")
    print(f"quantum-computing L500: per lesson {dict(sorted(per_lesson.items()))}")
    inventory = load("content/assessment/concept-inventory.json")
    if len(inventory) != 15:
        errs.append(f"concept inventory: {len(inventory)} items (want 15)")
    check_items("concept-inventory", inventory, {23}, errs, warns, seen_q, ids)
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    if errs:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
