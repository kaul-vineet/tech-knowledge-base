"""Validate content/qbank/L500.json (and the L500 concept inventory) with the same rules as ../tools/check_qbank.py,
which only reads L100-L400.

python research/check_l500_qbank.py      (from the astronomy folder; exit 1 on any error)
Rules (QBANK-SPEC + L500-SPEC): >= 40 questions; every lesson 23-27 has >= 6; required fields; level L500; lesson exists
in content/L500.json; valid type and difficulty; exactly 4 distinct options; answer index 0-3; no 'all/none of the
above'; explanation >= 30 characters; no duplicate ids or questions (across the bank and the inventory); each answer
position correct for 15-35 % of a file (spec target 20-30 %); warning if the correct option is the longest > 45 %.
The concept inventory must have exactly 15 items, lesson 23, ids distinct from the bank.
"""
import collections
import json
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)
FIELDS = ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source")


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def check_file(path, lessons, ids, seen_q, errs, warns, min_n=None, exact_n=None):
    qs = json.loads(path.read_text(encoding="utf-8"))
    name = path.relative_to(TOPIC).as_posix()
    if min_n is not None and len(qs) < min_n:
        errs.append(f"{name}: {len(qs)} questions (<{min_n})")
    if exact_n is not None and len(qs) != exact_n:
        errs.append(f"{name}: {len(qs)} questions (need exactly {exact_n})")
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
            errs.append(f"{qid}: level {q.get('level')} (want L500)")
        if q.get("lesson") not in lessons:
            errs.append(f"{qid}: lesson {q.get('lesson')} not in content/L500.json")
        if q.get("type") not in TYPES:
            errs.append(f"{qid}: bad type {q.get('type')}")
        if q.get("difficulty") not in (1, 2, 3):
            errs.append(f"{qid}: bad difficulty")
        opts = q.get("options", [])
        if len(opts) != 4 or len(set(map(norm, opts))) != 4:
            errs.append(f"{qid}: need 4 distinct options")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            errs.append(f"{qid}: bad answer index")
        if any(BANNED.search(o) for o in opts):
            errs.append(f"{qid}: 'all/none of the above' not allowed")
        if len(q.get("explanation", "")) < 30:
            errs.append(f"{qid}: explanation too short")
        if q.get("type") in ("code-reading", "debugging") and "code" in q and len(q["code"].splitlines()) > 15:
            errs.append(f"{qid}: code snippet longer than 15 lines")
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
                errs.append(f"{name}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30%)")
        longest = sum(1 for q in qs if len(q["options"]) == 4 and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
        if longest / n > 0.45:
            warns.append(f"{name}: correct option is the longest in {longest / n:.0%}")
    print(f"  {name}: {n} questions · types {dict(types)} · answers "
          f"{dict(sorted(('ABCD'[k], v) for k, v in pos.items() if isinstance(k, int) and 0 <= k < 4))} · per lesson {dict(sorted(per_lesson.items()))}")
    return per_lesson


def main():
    lessons = {les["number"] for les in json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))}
    errs, warns, ids, seen_q = [], [], set(), {}
    per_lesson = check_file(TOPIC / "content" / "qbank" / "L500.json", lessons, ids, seen_q, errs, warns, min_n=40)
    for num in sorted(lessons):
        if per_lesson[num] < 6:
            errs.append(f"lesson {num}: {per_lesson[num]} questions (<6)")
    inv = check_file(TOPIC / "content" / "assessment" / "concept-inventory.json", lessons, ids, seen_q, errs, warns, exact_n=15)
    if set(inv) != {23}:
        errs.append("concept inventory: every item must be lesson 23 (L500-SPEC)")
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    print("OK" if not errs else "FAILED")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
