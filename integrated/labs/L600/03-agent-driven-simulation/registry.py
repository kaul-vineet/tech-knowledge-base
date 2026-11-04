"""Experiment registry: append-only JSON lines. A run is identified by WHAT produced it, not when.

run_id = sha256(model name + model version + canonical params + seed). The result is stored as float.hex so
"reproducible" means bit-for-bit, and the environment fingerprint says where that promise holds.
"""
import hashlib
import json
from pathlib import Path

import model


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest(obj, n=16):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()[:n]


class Registry:
    def __init__(self, path=None):
        self.path, self.records, self._file = (Path(path) if path else None), [], None
        if self.path and self.path.exists():
            self.records = [json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x]

    def _append(self, rec):
        self.records.append(rec)
        if self.path:
            self._file = self._file or self.path.open("a", encoding="utf-8")
            self._file.write(canonical(rec) + "\n")
            self._file.flush()  # one line per record: a crash loses at most the line being written
        return rec

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def record_run(self, params, seed, value, job):
        params = {**model.DEFAULTS, **params}
        key = {"model": model.NAME, "version": model.VERSION, "params": params, "seed": seed}
        return self._append({"kind": "run", "run_id": digest(key), "params_hash": digest(params, 12), **key,
                             "value_hex": float(value).hex(), "env": model.ENVIRONMENT, "job": job})

    def record_experiment(self, exp_id, job, facts):
        """facts: {name: {"value": float, "runs": [run_id, ...]}} - every number the agent may quote."""
        return self._append({"kind": "experiment", "experiment_id": exp_id, "job": job, "facts": facts})

    def runs(self):
        return [r for r in self.records if r["kind"] == "run"]

    def run_ids(self):
        return {r["run_id"] for r in self.runs()}

    def experiment(self, exp_id):
        return next((r for r in self.records if r["kind"] == "experiment" and r["experiment_id"] == exp_id), None)


def reproduce(rec):
    """Re-run from the record alone; True only if the stored and new results are the same bits."""
    if rec["version"] != model.VERSION:
        return False  # model code changed since the run: the id no longer describes this code
    return model.run_once(rec["params"], rec["seed"]).hex() == rec["value_hex"]
