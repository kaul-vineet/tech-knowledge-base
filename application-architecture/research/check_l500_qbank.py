"""Validate the L500 question bank with the same rules as tools/check_qbank.py (which reads only L100-L400).

Run: python research/check_l500_qbank.py   (exit 1 on any error)
Checks content/qbank/L500.json (>= 40 items, >= 6 per lesson 23-27) and content/assessment/concept-inventory.json
(15 items, lesson 23), plus duplicates against the L100-L400 banks.
"""
import collections
import json
import pathlib
import re
import sys

TOPIC = pathlib.Path(__file__).resolve().parent.parent
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)
FIELDS = ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source")


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def check_items(label, qs, lessons, errs, warns, seen_q, ids, min_total, min_per_lesson):
    if len(qs) < min_total:
        errs.append(f"{label}: {len(qs)} questions (<{min_total})")
    pos, types, per_lesson = collections.Counter(), collections.Counter(), collections.Counter()
    for q in qs:
        qid = q.get("id", "?")
        errs += [f"{qid}: missing {k}" for k in FIELDS if k not in q]
        if qid in ids:
            errs.append(f"duplicate id {qid}")
        ids.add(qid)
        if q.get("level") != "L500":
            errs.append(f"{qid}: level {q.get('level')}")
        if q.get("lesson") not in lessons:
            errs.append(f"{qid}: lesson {q.get('lesson')} not in L500")
        if q.get("type") not in TYPES:
            errs.append(f"{qid}: bad type {q.get('type')}")
        if q.get("difficulty") not in (1, 2, 3):
            errs.append(f"{qid}: bad difficulty")
        options = q.get("options", [])
        if len(options) != 4 or len(set(map(norm, options))) != 4:
            errs.append(f"{qid}: need 4 distinct options")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            errs.append(f"{qid}: bad answer index")
        if any(BANNED.search(x) for x in options):
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
            errs.append(f"{label}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30%)")
        elif not 0.20 <= share <= 0.30:
            warns.append(f"{label}: answer {'ABCD'[a]} correct in {share:.0%} (target 20-30%)")
    longest = sum(1 for q in qs if len(q["options"]) == 4
                  and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    if n and longest / n > 0.45:
        warns.append(f"{label}: correct option is the longest in {longest / n:.0%}")
    for lesson in sorted(lessons):
        if min_per_lesson and per_lesson[lesson] < min_per_lesson:
            errs.append(f"{label}: lesson {lesson} has {per_lesson[lesson]} questions (<{min_per_lesson})")
    shares = {t: f"{c / n:.0%}" for t, c in sorted(types.items())}
    print(f"  {label}: {n} questions · types {shares} · answers "
          f"{dict(sorted(('ABCD'[k], v) for k, v in pos.items()))} · per lesson {dict(sorted(per_lesson.items()))} · "
          f"correct-is-longest {longest}")


def main():
    lessons = {lesson["number"] for lesson in json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))}
    errs, warns, ids, seen_q = [], [], set(), {}
    for level in ("L100", "L200", "L300", "L400"):  # earlier banks: only used to detect duplicates
        for q in json.loads((TOPIC / "content" / "qbank" / f"{level}.json").read_text(encoding="utf-8")):
            seen_q[norm(q["question"] + " " + q.get("code", ""))] = q["id"]
            ids.add(q["id"])
    bank = json.loads((TOPIC / "content" / "qbank" / "L500.json").read_text(encoding="utf-8"))
    check_items("L500", bank, lessons, errs, warns, seen_q, ids, 40, 6)
    inventory = json.loads((TOPIC / "content" / "assessment" / "concept-inventory.json").read_text(encoding="utf-8"))
    check_items("concept inventory", inventory, {23}, errs, warns, seen_q, ids, 15, 0)
    if len(inventory) != 15:
        errs.append(f"concept inventory: {len(inventory)} items (spec: 15)")
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    print("OK" if not errs else f"FAILED ({len(errs)} errors)")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
