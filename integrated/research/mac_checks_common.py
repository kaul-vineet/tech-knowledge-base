"""Shared helpers for checks_NN_mac.py: validate a qbank part (QBANK-SPEC rules), run code-reading snippets, and check
the macMini object of content/parts/NN.json against MAC-MINI-SPEC.md. Stdlib only."""
import contextlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # kb/integrated
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
BANNED = re.compile(r"\b(all|none) of the (above|options)\b", re.I)


def load_part(nn):
    return json.loads((ROOT / "content" / "parts" / f"{nn}.json").read_text(encoding="utf-8"))


def load_mac_bank(nn):
    return json.loads((ROOT / "content" / "qbank" / "parts" / f"{nn}-mac.json").read_text(encoding="utf-8"))


def check_bank(nn, bank, fails):
    if len(bank) < 6:
        fails.append(f"{nn}-mac: {len(bank)} questions (< 6)")
    for i, q in enumerate(bank, 1):
        qid = q.get("id")
        if qid != f"{nn}-mac-{i:02d}":
            fails.append(f"id {qid} (want {nn}-mac-{i:02d})")
        for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
            if k not in q:
                fails.append(f"{qid}: missing {k}")
        if q.get("level") != "L600" or q.get("lesson") != int(nn):
            fails.append(f"{qid}: level/lesson")
        if q.get("type") not in TYPES or q.get("difficulty") not in (1, 2, 3):
            fails.append(f"{qid}: type/difficulty")
        o = q.get("options", [])
        if len(o) != 4 or len({x.strip().lower() for x in o}) != 4 or any(BANNED.search(x) for x in o):
            fails.append(f"{qid}: options")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            fails.append(f"{qid}: answer index")
        if len(q.get("explanation", "")) < 30:
            fails.append(f"{qid}: explanation too short")
        if q.get("code") and len(q["code"].splitlines()) > 15:
            fails.append(f"{qid}: code longer than 15 lines")


def run_snippet(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<qbank>", "exec"), {})
    return buf.getvalue().strip()


def answer_text(q):
    return q["options"][q["answer"]]


def check_mac_mini(nn, fails):
    mm = load_part(nn).get("macMini")
    if not mm:
        fails.append(f"{nn}.json: no macMini")
        return None
    if set(mm) != {"gains", "needs", "experiments", "overnight", "validation"}:
        fails.append(f"{nn}.json macMini keys {sorted(mm)}")
    if not isinstance(mm["needs"].get("minRamGB"), int):
        fails.append("minRamGB not int")
    for t in mm["needs"].get("tools", []):
        if not {"name", "licence", "install"} <= set(t):
            fails.append(f"tool fields {t}")
    if not 2 <= len(mm["experiments"]) <= 3:
        fails.append("experiments count")
    for e in mm["experiments"]:
        if set(e) != {"title", "why", "steps", "measure", "decides"}:
            fails.append(f"experiment keys {sorted(e)}")
        for s in e["steps"]:
            if set(s) != {"title", "detail", "mac", "expected"}:
                fails.append(f"step keys {sorted(s)}")
    if set(mm["validation"]) != {"here", "pendingMac"} or not mm["validation"]["pendingMac"]:
        fails.append("validation")
    return mm
