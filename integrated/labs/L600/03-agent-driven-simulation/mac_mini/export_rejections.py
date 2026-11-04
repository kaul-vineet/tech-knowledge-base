"""Optional experiment (documented, not required): turn the proposals the contract REJECTED into a LoRA data set.

Reads 03-compare-models.jsonl (compare_models.py), keeps every tool call the CONTRACT rejected (budget refusals depend
on what ran before, so they are skipped), and RE-VALIDATES it with
contract.validate - the label is what the code says today, never what was logged. Writes mlx-lm "chat" data:
  <out>/train.jsonl, <out>/valid.jsonl   {"messages": [system, user = the proposal, assistant = the contract verdict]}
Each line teaches the model to predict the gate's answer. The gate stays: a fine-tuned model that proposes fewer bad
calls changes the rejection COUNT (compare_models.py again), never who decides.

python export_rejections.py --here                   uses the fake model's comparison (runs compare_models --here)
python export_rejections.py --runs ~/kb-runs --out ~/kb-runs/03-lora-data
Then on the Mac (mlx-lm, MIT; Apple silicon only):  see mac_mini/README.md, experiment "LoRA on rejections".
"""
import argparse
import json
import random
import sys
from pathlib import Path

import _lab
import agent
import contract

SYSTEM = "You check help-desk simulation proposals against the experiment contract before anything runs."


def verdict(tool, args):
    if not isinstance(args, dict):
        return "REJECTED: arguments are not a JSON object"
    problems = contract.validate(tool, args)
    return "VALID" if not problems else "REJECTED: " + "; ".join(problems)


def examples(compare_rows):
    out = []
    for row in compare_rows:
        for p in row.get("rejected_proposals", []):
            if p["errors"] and all(e.startswith("budget:") for e in p["errors"]):
                continue  # refused by the session budget, not the contract: depends on state, not on the proposal
            user = f"{agent.SYSTEM}\nProposal: {p['tool']} {json.dumps(p['args'], sort_keys=True)}"
            out.append({"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user},
                                     {"role": "assistant", "content": verdict(p["tool"], p["args"])}],
                        "source_model": row["model"]})
    return out


def split(items, valid_fraction=0.2, seed=3):
    items = sorted(items, key=lambda e: json.dumps(e, sort_keys=True))  # order-free input -> same split
    random.Random(seed).shuffle(items)
    k = int(round(len(items) * valid_fraction)) if len(items) >= 5 else 0
    return items[k:], items[:k]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--runs", help="folder with 03-compare-models.jsonl (default $KB_RUNS_DIR or ~/kb-runs)")
    ap.add_argument("--out", help="output folder for train.jsonl / valid.jsonl")
    a = ap.parse_args(argv)
    runs = _lab.runs_dir(a.runs)
    if a.here:
        import compare_models
        compare_models.main(["--here", "--out", str(runs)])
    rows = [json.loads(x) for x in (runs / "03-compare-models.jsonl").read_text(encoding="utf-8").splitlines() if x]
    ex = examples(rows)
    train, valid = split(ex)
    out = _lab.runs_dir(a.out or runs / "03-lora-data")
    _lab.write_jsonl(out / "train.jsonl", [{"messages": e["messages"]} for e in train])
    if valid:
        _lab.write_jsonl(out / "valid.jsonl", [{"messages": e["messages"]} for e in valid])
    print(json.dumps({"examples": len(ex), "train": len(train), "valid": len(valid), "out": str(out),
                      "verdicts": sorted({e["messages"][2]["content"][:60] for e in ex})}))
    if len(ex) < 100:
        print(f"only {len(ex)} examples: far too few for LoRA (hundreds+). Collect more by running "
              f"compare_models.py with more models every night (--out keeps one file per folder), or treat this "
              f"as a format check only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
