"""Validate content/qbank/L500.json with the same rules as tools/check_qbank.py (which reads only L100-L400), plus
content/assessment/concept-inventory.json (15 pre/post items, same schema, level L500, lesson 23).

python research/check_l500_qbank.py      (from the simulation/ folder; exit 1 on any error)
Calculation answers and code-reading outputs are recomputed separately by research/qbank_checks.py.
"""
import collections
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)
KEYS = ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source")


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def check_items(qs, label, lessons, errs, warns, seen_q, ids, min_n):
    if len(qs) < min_n:
        errs.append(f"{label}: {len(qs)} questions (<{min_n})")
    pos, types, per_lesson = collections.Counter(), collections.Counter(), collections.Counter()
    for q in qs:
        qid = q.get("id", "?")
        for k in KEYS:
            if k not in q:
                errs.append(f"{qid}: missing {k}")
        if qid in ids:
            errs.append(f"duplicate id {qid}")
        ids.add(qid)
        if q.get("level") != "L500":
            errs.append(f"{qid}: level {q.get('level')}")
        if q.get("lesson") not in lessons:
            errs.append(f"{qid}: lesson {q.get('lesson')} not an L500 lesson")
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
            errs.append(f"{qid}: snippet longer than 15 lines")
        key = norm(q.get("question", "") + " " + q.get("code", ""))
        if key in seen_q:
            errs.append(f"{qid}: duplicate of {seen_q[key]}")
        seen_q[key] = qid
        pos[q.get("answer")] += 1
        types[q.get("type")] += 1
        per_lesson[q.get("lesson")] += 1
    n = len(qs)
    if n:
        for a in range(4):
            share = pos[a] / n
            if not 0.15 <= share <= 0.35:
                errs.append(f"{label}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30%)")
        longest = sum(1 for q in qs if len(q["options"]) == 4 and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
        if longest / n > 0.45:
            warns.append(f"{label}: correct option is the longest in {longest / n:.0%}")
        mix = {t: f"{c / n:.0%}" for t, c in sorted(types.items())}
        print(f"  {label}: {n} questions · types {dict(types)} ({mix}) · answers "
              f"{dict(sorted(('ABCD'[k], v) for k, v in pos.items() if isinstance(k, int) and 0 <= k < 4))} · longest-correct {longest / n:.0%}")
    return per_lesson


def main():
    errs, warns, seen_q, ids = [], [], {}, set()
    lessons = {l["number"] for l in json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))}
    bank = json.loads((TOPIC / "content" / "qbank" / "L500.json").read_text(encoding="utf-8"))
    per_lesson = check_items(bank, "L500", lessons, errs, warns, seen_q, ids, 40)
    for num in sorted(lessons):
        if per_lesson[num] < 6:
            errs.append(f"lesson {num}: {per_lesson[num]} questions (<6)")
    print(f"  per lesson {dict(sorted(per_lesson.items()))}")
    ci = json.loads((TOPIC / "content" / "assessment" / "concept-inventory.json").read_text(encoding="utf-8"))
    check_items(ci, "concept inventory", lessons, errs, warns, seen_q, ids, 15)
    if len(ci) != 15:
        errs.append(f"concept inventory: {len(ci)} items (spec: 15)")
    if any(q.get("lesson") != 23 for q in ci):
        errs.append("concept inventory: every item must be lesson 23")
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    print("OK" if not errs else f"{len(errs)} errors")
    return not errs


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
