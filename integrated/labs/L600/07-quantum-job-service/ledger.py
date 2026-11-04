"""Shipped ledger (UNFIXED - the failure lab and your build task).

Every completion that arrives is merged. Under at-least-once delivery a chunk whose lease expired on a slow backend
runs twice, both attempts report, and the job returns more shots than requested.
Build task: copy this file to my_ledger.py and make write() idempotent and fenced (see README); then
  macOS:   BUILD_TARGET=mine python -m unittest discover -s tests -p "test_build_task.py" -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest discover -s tests -p "test_build_task.py" -v
"""
from jobstore import JobStore


class Ledger(JobStore):
    def new_slot(self):
        return []

    def write(self, slot, token, counts):
        slot.append(counts)                     # every attempt's counts are kept and later merged
        return "accepted"

    def read(self, slot):
        if not slot:
            return None
        merged = {}
        for counts in slot:
            for k, v in counts.items():
                merged[k] = merged.get(k, 0) + v
        return merged
