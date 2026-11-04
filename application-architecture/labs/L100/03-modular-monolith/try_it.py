"""Try it (lesson 3): break a module boundary on a scratch copy and watch the fitness test fail.
Run: python try_it.py
"""
import pathlib
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / ".tryit-work"


def remove_scratch():
    for _ in range(5):  # retry: some network mounts need a second pass
        shutil.rmtree(WORK, ignore_errors=True)
        if not WORK.exists():
            return
        time.sleep(0.5)


def scratch_copy_with(shortcut_source):
    remove_scratch()
    shutil.copytree(HERE, WORK, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns(".tryit-work", "__pycache__", "try_it.py"))
    (WORK / "library" / "loans" / "shortcut.py").write_text(shortcut_source, encoding="utf-8")
    return WORK


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=WORK, capture_output=True, text=True, encoding="utf-8")


def try_1_relative_import_breaks_boundary():
    scratch_copy_with("from ..catalog.internal import store\n")
    check = run("check_boundaries.py")
    print(f"[1] check_boundaries.py -> exit {check.returncode}")
    print("    " + check.stdout.strip().replace("\n", "\n    "))
    tests = run("-m", "unittest")
    print(f"[1] python -m unittest -> exit {tests.returncode}; {tests.stderr.strip().splitlines()[-1]}")
    for line in tests.stderr.splitlines():
        if line.startswith("FAIL:"):
            print("    " + line)


def try_2_dynamic_import_slips_through():
    scratch_copy_with('import importlib\nstore = importlib.import_module("library.catalog.internal.store")\n')
    check = run("check_boundaries.py")
    print(f"[2] importlib.import_module(...) -> exit {check.returncode}; {check.stdout.strip()}")


if __name__ == "__main__":
    try:
        try_1_relative_import_breaks_boundary()
        try_2_dynamic_import_slips_through()
    finally:
        remove_scratch()
