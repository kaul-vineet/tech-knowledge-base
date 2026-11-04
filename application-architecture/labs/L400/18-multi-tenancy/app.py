"""Lesson 18 demo: measure isolation, noisy neighbour and migration effort for three tenancy layouts.

Run: python app.py              (base repository.py: the new overdue report forgot tenant_id)
     python app.py --solution   (fixed repository)
Writes out/tenancy.jsonl (one JSON line per layout) and prints the same rows.
"""
import argparse
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import time

import tenancy

HERE = pathlib.Path(__file__).resolve().parent
TENANTS = [f"lib{i:02d}" for i in range(50)]


def use_repository(path):
    spec = importlib.util.spec_from_file_location("repository", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["repository"] = tenancy.repository = module  # the layouts call whichever repository is loaded
    return module


def measure(layout_cls, work, tenants=TENANTS):
    layout = layout_cls(work)
    tenancy.seed(layout, tenants)
    row = {"layout": layout.kind, "isolation": tenancy.leak_check(layout, "lib00"),
           "noisy_neighbour": tenancy.noisy_neighbour(layout, "lib01", "lib02")}
    start = time.perf_counter()
    row["migration"] = tenancy.migrate(layout, tenants)
    row["migration"]["ms"] = round((time.perf_counter() - start) * 1000, 1)  # informational: varies by disk
    return row


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", action="store_true")
    use_repository(HERE / ("solution/repository.py" if parser.parse_args(argv).solution else "repository.py"))
    (HERE / "out").mkdir(exist_ok=True)
    rows = []
    for layout_cls in tenancy.LAYOUTS:
        work = pathlib.Path(tempfile.mkdtemp(prefix=".work-", dir=HERE))
        try:
            rows.append(measure(layout_cls, work))
        finally:
            shutil.rmtree(work, ignore_errors=True)
        print(json.dumps(rows[-1]))
    (HERE / "out" / "tenancy.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return rows


if __name__ == "__main__":
    main()
