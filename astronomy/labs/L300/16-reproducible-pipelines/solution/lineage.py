"""Stretch solution (lesson 16): answer 'where did this number come from?' from prov.jsonl alone.

lineage(prov_lines, generated_sha) walks generated -> upstream records back to the raw input file's hash
and lists every activity with its parameters and code version. python solution/lineage.py
"""
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def lineage(prov_lines, generated_sha):
    by_output = {}
    for line in prov_lines:
        rec = json.loads(line)
        by_output.setdefault(rec["generated_sha256"], rec)  # first record that produced this output
    chain, sha = [], generated_sha
    while sha in by_output:
        rec = by_output[sha]
        chain.append({"activity": rec["activity"], "params": rec["params"], "code_sha256": rec["code_sha256"],
                      "input_file_sha256": rec["used"]["sha256"]})
        sha = rec["upstream_sha256"]
    return chain


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("pipeline_fixed", HERE / "pipeline.py")
    pipe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipe)
    with tempfile.TemporaryDirectory() as tmp:
        pipe.demo(Path(tmp))
        lines = (Path(tmp) / "prov.jsonl").read_text(encoding="utf-8").splitlines()
    final = json.loads(lines[-1])["generated_sha256"]
    for step in lineage(lines, final):
        print(json.dumps(step))
