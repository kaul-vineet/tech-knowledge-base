"""Try it (lesson 4): create contract drift on a scratch copy and watch the contract test fail.
Run: python try_it.py
"""
import pathlib
import shutil
import subprocess
import sys
import time

from contract_check import check, load_spec

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / ".tryit-work"


def remove_scratch():
    for _ in range(5):  # retry: some network mounts need a second pass
        shutil.rmtree(WORK, ignore_errors=True)
        if not WORK.exists():
            return
        time.sleep(0.5)


def try_1_rename_field():
    remove_scratch()
    shutil.copytree(HERE, WORK, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns(".tryit-work", "__pycache__", "try_it.py"))
    server = WORK / "server.py"
    source = server.read_text(encoding="utf-8")
    server.write_text(source.replace('"memberId": member', '"member": member'), encoding="utf-8")  # drift: field renamed
    run = subprocess.run([sys.executable, "-m", "unittest"], cwd=WORK, capture_output=True, text=True, encoding="utf-8")
    print(f"[1] memberId renamed to member -> exit {run.returncode}; {run.stderr.strip().splitlines()[-1]}")
    for line in run.stderr.splitlines():
        if line.startswith(("FAIL:", "AssertionError")):
            print("    " + line.strip())


def try_2_undeclared_status():
    spec = load_spec()
    print("[2] POST /loans answered 500 ->", check(spec, "POST", "/loans", 500, {"error": "boom"}))
    print("[2] POST /loans answered 409 ->", check(spec, "POST", "/loans", 409, {"error": "on loan"}))


if __name__ == "__main__":
    try:
        try_1_rename_field()
        try_2_undeclared_status()
    finally:
        remove_scratch()
