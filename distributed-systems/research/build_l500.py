"""Builds content/L500.json (lessons 23-27). python research/build_l500.py

Every theorem's checkOutput is the real stdout of its check command, captured when this script runs
(research/l500_checks.py re-runs the commands and fails if the stored output drifts).
Lesson text lives in research/l500_lessons_*.py; this file only assembles and writes.
"""
import json
import shlex
import subprocess
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from l500_lessons_foundations import LESSON_23, LESSON_24, LESSON_25  # noqa: E402
from l500_lessons_humanities import LESSON_26, LESSON_27  # noqa: E402


def run(cmd):
    parts = shlex.split(cmd)
    script = TOPIC / parts[0]
    out = subprocess.run([sys.executable, script.name, *parts[1:]], cwd=script.parent,
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return out.stdout.strip()


def main():
    lessons = [LESSON_23, LESSON_24, LESSON_25, LESSON_26, LESSON_27]
    for lesson in lessons:
        for th in lesson.get("theorems", []):
            th["checkOutput"] = run(th["check"])
    path = TOPIC / "content" / "L500.json"
    if path.exists():
        path.unlink()  # the mount breaks in-place rewrites: delete, then write
    path.write_text(json.dumps(lessons, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(TOPIC)}: {len(lessons)} lessons, "
          f"{sum(len(l.get('theorems', [])) for l in lessons)} theorems, "
          f"{sum(len(l.get('problemSet', [])) for l in lessons)} problems")


if __name__ == "__main__":
    main()
