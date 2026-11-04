"""Validate a topic's question bank: python tools/check_qbank.py <topic> [<topic> ...]   (exit 1 on any error)"""
import json, re, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)
def norm(s): return re.sub(r"\W+", " ", s.lower()).strip()
def check(topic):
    errs, warns, total = [], [], 0
    lessons = {}
    for lv in ["L100", "L200", "L300", "L400"]:
        for l in json.loads((ROOT / topic / "content" / f"{lv}.json").read_text(encoding="utf-8")):
            lessons[l["number"]] = lv
    per_lesson = collections.Counter(); seen_q = {}; ids = set()
    for lv in ["L100", "L200", "L300", "L400"]:
        p = ROOT / topic / "content" / "qbank" / f"{lv}.json"
        if not p.exists(): errs.append(f"missing {p.relative_to(ROOT)}"); continue
        qs = json.loads(p.read_text(encoding="utf-8"))
        if len(qs) < 40: errs.append(f"{lv}: {len(qs)} questions (<40)")
        pos = collections.Counter(); types = collections.Counter()
        for q in qs:
            qid = q.get("id", "?")
            for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
                if k not in q: errs.append(f"{qid}: missing {k}")
            if qid in ids: errs.append(f"duplicate id {qid}")
            ids.add(qid)
            if q.get("level") != lv: errs.append(f"{qid}: level {q.get('level')} in {lv} file")
            if lessons.get(q.get("lesson")) != lv: errs.append(f"{qid}: lesson {q.get('lesson')} not in {lv}")
            if q.get("type") not in TYPES: errs.append(f"{qid}: bad type {q.get('type')}")
            if q.get("difficulty") not in (1, 2, 3): errs.append(f"{qid}: bad difficulty")
            o = q.get("options", [])
            if len(o) != 4 or len(set(map(norm, o))) != 4: errs.append(f"{qid}: need 4 distinct options")
            if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3: errs.append(f"{qid}: bad answer index")
            if any(BANNED.search(x) for x in o): errs.append(f"{qid}: 'all/none of the above' not allowed")
            if len(q.get("explanation", "")) < 30: errs.append(f"{qid}: explanation too short")
            k = norm(q.get("question", "") + " " + q.get("code", ""))
            if k in seen_q: errs.append(f"{qid}: duplicate of {seen_q[k]}")
            seen_q[k] = qid
            pos[q.get("answer")] += 1; types[q.get("type")] += 1; per_lesson[q.get("lesson")] += 1
        n = len(qs); total += n
        if n:
            for a in range(4):
                share = pos[a] / n
                if not 0.15 <= share <= 0.35: errs.append(f"{lv}: answer {'ABCD'[a]} correct in {share:.0%} (want 20-30%)")
            longest = sum(1 for q in qs if len(q["options"]) == 4 and max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
            if longest / n > 0.45: warns.append(f"{lv}: correct option is the longest in {longest/n:.0%}")
        print(f"  {lv}: {n} questions · types {dict(types)} · answers {dict(sorted((('ABCD'[k] if isinstance(k,int) and 0<=k<4 else k),v) for k,v in pos.items()))}")
    for num, lv in sorted(lessons.items()):
        need = 4 if num == 1 else 6
        if per_lesson[num] < need: errs.append(f"lesson {num}: {per_lesson[num]} questions (<{need})")
    print(f"{topic}: {total} questions; per lesson {dict(sorted(per_lesson.items()))}")
    for w in warns: print("  WARN", w)
    for e in errs: print("  ERROR", e)
    return not errs
if __name__ == "__main__":
    ok = all([check(t) for t in sys.argv[1:]])
    sys.exit(0 if ok else 1)
