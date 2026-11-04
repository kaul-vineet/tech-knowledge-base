"""Try it (lesson 11): measure the layers, then plant two bugs and see which layer catches each. Run: python try_it.py

Bugs go into a temporary copy (.tryit-work/); the lab files are never edited.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / ".tryit-work"
BUGS = {"sqlite_store.py: bool(row[3]) -> row[3]": ("sqlite_store.py", "bool(row[3])", "row[3]"),
        "http_api.py: BookAlreadyOnLoan 409 -> 422": ("http_api.py", "BookAlreadyOnLoan: 409", "BookAlreadyOnLoan: 422")}


def remove_scratch():
    for _ in range(5):  # retry: some network mounts need a second pass
        shutil.rmtree(WORK, ignore_errors=True)
        if not WORK.exists():
            return
        time.sleep(0.5)


def run_pyramid(cwd):
    run = subprocess.run([sys.executable, "pyramid.py"], cwd=cwd, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                         capture_output=True, text=True, encoding="utf-8")
    return run.stdout


def try_1_measure():
    out = run_pyramid(HERE)
    means = dict(re.findall(r"^(unit|integration|e2e)\s+\d+\s+\d+\s+\d+\s+[\d.]+\s+([\d.]+)$", out, re.M))
    ratio = re.search(r"as much as ([\d,]+) unit tests \(about (10\^\d+)\)", out)
    print(f"[1] mean ms: unit {means['unit']}, integration {means['integration']}, e2e {means['e2e']} "
          f"-> one e2e test = {ratio.group(1)} unit tests ({ratio.group(2)})")


def try_2_which_layer_catches_it():
    for label, (filename, old, new) in BUGS.items():
        remove_scratch()
        WORK.mkdir()
        for path in HERE.glob("*.py"):
            shutil.copyfile(path, WORK / path.name)
        target = WORK / filename
        target.write_text(target.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
        failed = dict(re.findall(r"^(unit|integration|e2e)\s+\d+\s+\d+\s+(\d+)", run_pyramid(WORK), re.M))
        print(f"[2] {label:<44} failed tests -> unit {failed['unit']}, integration {failed['integration']}, "
              f"e2e {failed['e2e']}")


if __name__ == "__main__":
    try:
        try_1_measure()
        try_2_which_layer_catches_it()
    finally:
        remove_scratch()
