"""Build content/L500.json from research/l500_data_*.py, inserting the REAL output of each theorem check.
Run from the topic folder or anywhere: python research/build_l500.py
(re-run after changing a check; research/l500_checks.py then verifies the stored outputs still match)."""
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOPIC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from l500_data_23_25 import L23, L24, L25  # noqa: E402
from l500_data_26_27 import L26, L27  # noqa: E402


def sections(script: str) -> dict:
    """Run a theorem_checks.py and split its stdout into {'T23.1': text, ...} by '[ID]' header lines."""
    path = TOPIC / script
    out = subprocess.run([sys.executable, "-B", path.name], cwd=path.parent, capture_output=True, text=True,
                         timeout=600, check=True).stdout
    result, current = {}, None
    for line in out.splitlines():
        if line.startswith("[") and "]" in line:
            current = line[1:line.index("]")]
            result[current] = [line]
        elif current:
            result[current].append(line)
    return {k: "\n".join(v) for k, v in result.items()}


def main() -> None:
    lessons = [L23, L24, L25, L26, L27]
    cache = {}
    for lesson in lessons[:3]:
        for th in lesson["theorems"]:
            if th["check"] not in cache:
                cache[th["check"]] = sections(th["check"])
            th["checkOutput"] = cache[th["check"]][th["id"]]
        lab = Path(lesson["theorems"][0]["check"]).parent
        demo = {k: v for k, v in cache[lesson["theorems"][0]["check"]].items() if k.startswith("D")}
        if demo:
            lesson["demoOutput"] = "\n".join(demo.values())
        lesson["validation"] = {
            "status": "validated-local",
            "how": f"Ran {lab}/theorem_checks.py (output stored verbatim in each theorem's checkOutput), the lab's main "
                   f"script and `python -m unittest` locally on Linux, Python 3.12, cryptography 50.0.2; "
                   f"research/l500_checks.py re-runs the checks and recomputes every calculation answer.",
            "pendingCi": "macOS (arm64) and Windows jobs in .github/workflows/labs.yml (L500 step) have not run yet.",
        }
    for lesson in lessons[3:]:
        lesson["validation"] = {
            "status": "validated-local",
            "how": "No code. Every source URL was retrieved on 2026-10-30 (see research/L500-evidence.md); calculation "
                   "answers in the problem set are recomputed by research/l500_checks.py.",
            "pendingCi": "none (no lab code)",
        }
    order = ["id", "number", "level", "title", "phase", "category", "description", "outcome", "environment",
             "estimatedTime", "prerequisites", "learningObjectives", "glossary", "theorems", "demoOutput", "caseStudy",
             "readings", "problemSet", "rubric", "steps", "codeLanguage", "projectFiles", "caution", "conceptNote",
             "conceptSummary", "sources", "seeAlso", "next", "platforms", "validation"]
    out = [{k: l[k] for k in order if k in l} | {k: v for k, v in l.items() if k not in order} for l in lessons]
    target = TOPIC / "content" / "L500.json"
    if target.exists():
        target.unlink()  # the mount breaks in-place rewrites: delete then write
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {target.relative_to(TOPIC)}: {len(out)} lessons, "
          f"{sum(len(l.get('theorems', [])) for l in out)} theorems, {sum(len(l['problemSet']) for l in out)} problems")


if __name__ == "__main__":
    main()
