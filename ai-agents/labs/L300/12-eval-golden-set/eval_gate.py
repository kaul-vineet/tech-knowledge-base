"""Golden-set evaluation + regression gate for a ticket-triage prompt (exit code 1 = block the merge)."""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
FIELDS = {"category": {"billing", "technical", "account", "shipping", "other"}, "priority": {"high", "normal"}}
RUBRIC_MIN = 2 / 3  # rubric = checklist scored 0..1; a case needs 2 of 3 points


def load_cases(path=HERE / "golden.jsonl"):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def run_case(prompt, case, base_url=BASE_URL, model=MODEL):
    text = prompt.replace("{{ticket}}", case["ticket"])  # same placeholder syntax as promptfoo
    r = requests.post(f"{base_url}/chat/completions", timeout=60, json={
        "model": model, "messages": [{"role": "user", "content": text}], "temperature": 0})
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def check(case, output):
    """Structural, exact and rubric checks. Returns the reasons it failed (empty list = pass)."""
    try:
        data = json.loads(output)
    except ValueError:
        return ["structural: not JSON"]
    if not isinstance(data, dict):
        return ["structural: not a JSON object"]
    problems = [] if set(data) == {*FIELDS, "summary"} else [f"structural: keys {sorted(data)}"]
    for field, allowed in FIELDS.items():  # structural: values from the allowed set
        if data.get(field) not in allowed:
            problems.append(f"structural: {field}={data.get(field)!r} not allowed")
        elif data[field] != case["expect"][field]:  # exact: the labelled answer
            problems.append(f"exact: {field}={data[field]!r}, expected {case['expect'][field]!r}")
    summary = str(data.get("summary", ""))
    points = [len(summary.split()) <= 12, case["rubric"]["mentions"].lower() in summary.lower(),
              "sorry" not in summary.lower()]  # rubric: a scored checklist, not all-or-nothing
    if sum(points) / len(points) < RUBRIC_MIN:
        problems.append(f"rubric: {sum(points)}/{len(points)} points")
    return problems


def evaluate(prompt_path, cases=None, base_url=BASE_URL, model=MODEL):
    prompt = Path(prompt_path).read_text(encoding="utf-8")
    results = {}
    for case in cases or load_cases():
        problems = check(case, run_case(prompt, case, base_url, model))
        results[case["id"]] = {"pass": not problems, "problems": problems, "category": case["expect"]["category"]}
    passed = sum(r["pass"] for r in results.values())
    return {"prompt": Path(prompt_path).name, "passed": passed, "total": len(results),
            "pass_rate": round(passed / len(results), 3), "results": results}


def gate(report, baseline, min_pass_rate=0.95):
    """Regression gate: block if the pass rate drops below the bar OR any case that passed before now fails."""
    regressions = [cid for cid, r in report["results"].items()
                   if baseline["results"].get(cid, {}).get("pass") and not r["pass"]]
    reasons = [f"pass rate {report['pass_rate']:.0%} < {min_pass_rate:.0%}"] if report["pass_rate"] < min_pass_rate else []
    return reasons + ([f"regressions vs baseline: {regressions}"] if regressions else [])


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", default=str(HERE / "prompts" / "v1.txt"))
    p.add_argument("--baseline", default=str(HERE / "baseline.json"))
    p.add_argument("--min-pass-rate", type=float, default=0.95)
    p.add_argument("--write-baseline", action="store_true")
    a = p.parse_args(argv)
    report = evaluate(a.prompt)
    for cid, r in report["results"].items():
        if not r["pass"]:
            print(f"FAIL {cid} ({r['category']}): {'; '.join(r['problems'])}")
    print(f"{report['prompt']}: {report['passed']}/{report['total']} passed ({report['pass_rate']:.0%})")
    if a.write_baseline:
        Path(a.baseline).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print(f"baseline written: {Path(a.baseline).name}")
        return 0
    reasons = gate(report, json.loads(Path(a.baseline).read_text(encoding="utf-8")), a.min_pass_rate)
    print("GATE: " + ("BLOCK - " + " | ".join(reasons) if reasons else "PASS"))
    return 1 if reasons else 0


if __name__ == "__main__":
    sys.exit(main())
