"""Flatten trace.jsonl into spans.csv (one row per span) for a spreadsheet or Orange. Run: python spans_to_csv.py"""
import csv
import json
import sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "trace.jsonl")
dst = Path(sys.argv[2] if len(sys.argv) > 2 else "spans.csv")
with dst.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "operation", "kind", "start_ms", "duration_ms", "input_tokens", "output_tokens", "status"])
    for line in src.read_text(encoding="utf-8").splitlines():
        s = json.loads(line)
        a = s["attributes"]
        w.writerow([s["name"], a.get("gen_ai.operation.name"), s["kind"], s["start_ms"], s["duration_ms"],
                    a.get("gen_ai.usage.input_tokens", ""), a.get("gen_ai.usage.output_tokens", ""), s["status"]])
print(f"wrote {dst} ({len(src.read_text(encoding='utf-8').splitlines())} spans)")
