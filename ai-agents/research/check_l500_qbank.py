"""Validate content/qbank/L500.json with the rules of kb/tools/check_qbank.py (which reads only L100-L400),
and content/assessment/concept-inventory.json with the same per-item rules.

    python research/check_l500_qbank.py      -> exit 1 on any error

Rules: >= 40 questions, every L500 lesson (23-27) >= 6; required fields; level L500; lesson exists in content/L500.json;
type in the allowed set; difficulty 1-3; exactly 4 distinct options; answer index 0-3; no 'all/none of the above';
explanation >= 30 chars; no duplicate ids or questions; each answer position correct for 15-35 % of items (target 20-30 %);
warning if the correct option is the longest in > 45 % of items. Also reports the type mix.
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


def check_items(name, qs, lessons, errs, warns, min_total, min_per_lesson):
    pos, types, per_lesson, ids, seen = (collections.Counter(), collections.Counter(), collections.Counter(), set(), {})
    if len(qs) < min_total:
        errs.append(f"{name}: {len(qs)} questions (<{min_total})")
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
        key = norm(q.get("question", "") + " " + q.get("code", ""))
        if key in seen:
            errs.append(f"{qid}: duplicate of {seen[key]}")
        seen[key] = qid
        pos[q.get("answer")] += 1
        types[q.get("type")] += 1
        per_lesson[q.get("lesson")] += 1
    n = len(qs)
    if n:
        for a in range(4):
            share = pos[a] / n
            if not 0.15 <= share <= 0.35:
                errs.append(f"{name}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30 %)")
        longest = sum(1 for q in qs if len(q["options"]) == 4 and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
        if longest / n > 0.45:
            warns.append(f"{name}: correct option is the longest in {longest / n:.0%}")
        print(f"  {name}: {n} items · longest-is-correct {longest}/{n} · types {dict(types)} · "
              f"answers {dict(sorted(('ABCD'[k], v) for k, v in pos.items() if isinstance(k, int) and 0 <= k < 4))}")
    if min_per_lesson:
        for num in sorted(lessons):
            if per_lesson[num] < min_per_lesson:
                errs.append(f"{name}: lesson {num}: {per_lesson[num]} questions (<{min_per_lesson})")
        print(f"  {name}: per lesson {dict(sorted(per_lesson.items()))}")
    return ids


def main():
    errs, warns = [], []
    lessons = {l["number"] for l in json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))}
    bank = json.loads((TOPIC / "content" / "qbank" / "L500.json").read_text(encoding="utf-8"))
    ids = check_items("qbank/L500.json", bank, lessons, errs, warns, 40, 6)
    ci_path = TOPIC / "content" / "assessment" / "concept-inventory.json"
    if ci_path.exists():
        ci = json.loads(ci_path.read_text(encoding="utf-8"))
        ci_ids = check_items("assessment/concept-inventory.json", ci, lessons, errs, warns, 15, 0)
        if ids & ci_ids:
            errs.append(f"concept inventory reuses qbank ids {sorted(ids & ci_ids)}")
        bank_q = {norm(q["question"]) for q in bank}
        for q in ci:
            if norm(q["question"]) in bank_q:
                errs.append(f"{q['id']}: concept-inventory item duplicates a qbank question")
    else:
        errs.append("missing content/assessment/concept-inventory.json")
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    print("OK" if not errs else f"{len(errs)} error(s)")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
