"""Build content/qbank/L100-L500.json from tools/qbank_L*.py, and content/assessment/concept-inventory.json.

Run:  python tools/build_qbank.py      (numpy only; computes every calculation value with labs/_shared/qsim)
Each data module lists the correct option first; this script moves it to a balanced, seeded position
(each of A-D correct for 10-11 of a level's questions) and writes the files fresh (delete, then write).
Verify afterwards: python research/qbank_checks.py, python research/check_l500_qbank.py  and  (from kb/) python tools/check_qbank.py quantum-computing
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import qbank_L100  # noqa: E402
import qbank_L200  # noqa: E402
import qbank_L300  # noqa: E402
import qbank_L400  # noqa: E402
import qbank_L500  # noqa: E402
import concept_inventory  # noqa: E402

OUT = HERE.parent / "content" / "qbank"
LEVELS = {"L100": qbank_L100, "L200": qbank_L200, "L300": qbank_L300, "L400": qbank_L400, "L500": qbank_L500}
INVENTORY = HERE.parent / "content" / "assessment" / "concept-inventory.json"
KEYS = ("id", "level", "lesson", "type", "difficulty", "question", "code", "options", "answer", "explanation", "source")


def place(questions, level, seed=None):
    n = len(questions)
    positions = [i % 4 for i in range(n)]
    random.Random(seed or f"qc-{level}").shuffle(positions)
    out = []
    for q, pos in zip(questions, positions):
        correct, wrong = q["options"][0], q["options"][1:]
        options = wrong[:pos] + [correct] + wrong[pos:]
        row = {**q, "level": level, "options": options, "answer": pos}
        out.append({k: row[k] for k in KEYS if k in row})
    return out


def write(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    longest = sum(1 for q in rows if max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
    print(f"{path.relative_to(HERE.parent)}: {len(rows)} questions; correct is longest in {longest}/{len(rows)}")


def main():
    for level, module in LEVELS.items():
        write(place(module.QUESTIONS, level), OUT / f"{level}.json")
    write(place(concept_inventory.QUESTIONS, "L500", seed="qc-CI"), INVENTORY)


if __name__ == "__main__":
    main()
