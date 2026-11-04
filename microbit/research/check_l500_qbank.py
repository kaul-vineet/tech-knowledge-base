"""Validate content/qbank/L500.json with the same rules as kb/tools/check_qbank.py (which reads only
L100-L400), plus the L500 spec: >= 40 questions, >= 6 per lesson 23-27, answer positions 20-30 %.
Also validates content/assessment/concept-inventory.json (15 pre/post items, same schema).

Run from the topic root:  python research/check_l500_qbank.py   (Windows: py research\\check_l500_qbank.py)  -> exit 0
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOPIC = os.path.dirname(HERE)
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def main():
    errs, warns = [], []
    with open(os.path.join(TOPIC, "content", "L500.json"), encoding="utf-8") as fh:
        lessons = {les["number"] for les in json.load(fh)}
    seen_q, ids = {}, set()
    for lv in ("L100", "L200", "L300", "L400"):          # no near-duplicates of earlier levels either
        with open(os.path.join(TOPIC, "content", "qbank", lv + ".json"), encoding="utf-8") as fh:
            for q in json.load(fh):
                seen_q[norm(q["question"] + " " + q.get("code", ""))] = q["id"]
                ids.add(q["id"])
    with open(os.path.join(TOPIC, "content", "qbank", "L500.json"), encoding="utf-8") as fh:
        qs = json.load(fh)
    if len(qs) < 40:
        errs.append("L500: %d questions (<40)" % len(qs))
    pos, types, per_lesson, diffs = (collections.Counter() for _ in range(4))
    for q in qs:
        qid = q.get("id", "?")
        for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
            if k not in q:
                errs.append("%s: missing %s" % (qid, k))
        if qid in ids:
            errs.append("duplicate id %s" % qid)
        ids.add(qid)
        if not re.fullmatch(r"mb-L500-\d{3}", qid):
            errs.append("%s: id format" % qid)
        if q.get("level") != "L500":
            errs.append("%s: level %s" % (qid, q.get("level")))
        if q.get("lesson") not in lessons:
            errs.append("%s: lesson %s not in L500" % (qid, q.get("lesson")))
        if q.get("type") not in TYPES:
            errs.append("%s: bad type %s" % (qid, q.get("type")))
        if q.get("difficulty") not in (1, 2, 3):
            errs.append("%s: bad difficulty" % qid)
        o = q.get("options", [])
        if len(o) != 4 or len(set(map(norm, o))) != 4:
            errs.append("%s: need 4 distinct options" % qid)
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            errs.append("%s: bad answer index" % qid)
        if any(BANNED.search(x) for x in o):
            errs.append("%s: 'all/none of the above' not allowed" % qid)
        if len(q.get("explanation", "")) < 30:
            errs.append("%s: explanation too short" % qid)
        if q.get("code") and len(q["code"].rstrip("\n").splitlines()) > 15:
            errs.append("%s: snippet longer than 15 lines" % qid)
        k = norm(q.get("question", "") + " " + q.get("code", ""))
        if k in seen_q:
            errs.append("%s: duplicate of %s" % (qid, seen_q[k]))
        seen_q[k] = qid
        pos[q.get("answer")] += 1
        types[q.get("type")] += 1
        per_lesson[q.get("lesson")] += 1
        diffs[q.get("difficulty")] += 1
    n = len(qs)
    for a in range(4):
        share = pos[a] / n if n else 0
        if not 0.20 <= share <= 0.30:
            errs.append("answer %s correct in %.0f%% (want 20-30%%)" % ("ABCD"[a], 100 * share))
    longest = sum(1 for q in qs if len(q["options"]) == 4
                  and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    if n and longest / n > 0.45:
        warns.append("correct option is the longest in %.0f%%" % (100 * longest / n))
    for num in sorted(lessons):
        if per_lesson[num] < 6:
            errs.append("lesson %d: %d questions (<6)" % (num, per_lesson[num]))
    mix = {t: "%d (%.0f%%)" % (c, 100 * c / n) for t, c in sorted(types.items())}
    print("L500: %d questions; per lesson %s" % (n, dict(sorted(per_lesson.items()))))
    print("  types %s" % mix)
    print("  answers %s; difficulty %s; correct-is-longest %.0f%%" % (
        {"ABCD"[k]: v for k, v in sorted(pos.items())}, dict(sorted(diffs.items())), 100 * longest / n if n else 0))
    errs += check_concept_inventory()
    for w in warns:
        print("  WARN", w)
    for e in errs:
        print("  ERROR", e)
    print("OK" if not errs else "FAILED")
    return 0 if not errs else 1


def check_concept_inventory():
    """content/assessment/concept-inventory.json: 15 pre/post items, qbank schema, level L500, lesson 23."""
    errs = []
    with open(os.path.join(TOPIC, "content", "assessment", "concept-inventory.json"), encoding="utf-8") as fh:
        items = json.load(fh)
    if len(items) != 15:
        errs.append("concept inventory: %d items (want 15)" % len(items))
    pos = collections.Counter()
    for q in items:
        qid = q.get("id", "?")
        for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
            if k not in q:
                errs.append("%s: missing %s" % (qid, k))
        if q.get("level") != "L500" or q.get("lesson") != 23 or q.get("type") not in TYPES:
            errs.append("%s: level/lesson/type" % qid)
        o = q.get("options", [])
        if len(o) != 4 or len(set(map(norm, o))) != 4 or any(BANNED.search(x) for x in o):
            errs.append("%s: options" % qid)
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            errs.append("%s: answer" % qid)
        pos[q.get("answer")] += 1
    if any(not 2 <= pos[a] <= 5 for a in range(4)):
        errs.append("concept inventory: answer positions unbalanced %s" % dict(pos))
    longest = sum(1 for q in items if max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    print("concept inventory: %d items; answers %s; correct-is-longest %d" % (
        len(items), {"ABCD"[k]: v for k, v in sorted(pos.items())}, longest))
    if longest > 6:
        errs.append("concept inventory: correct option is the longest in %d items" % longest)
    return errs


if __name__ == "__main__":
    sys.exit(main())
