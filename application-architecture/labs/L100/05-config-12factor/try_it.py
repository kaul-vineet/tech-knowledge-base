"""Try it (lesson 5): two config experiments; code changes happen on a scratch copy. Run: python try_it.py"""
import os
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
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("LOANS_")}


def run(cwd, *args, env=None):
    return subprocess.run([sys.executable, *args], cwd=cwd, env={**CLEAN_ENV, **(env or {})},
                          capture_output=True, text=True, encoding="utf-8")


def try_1_lowercase_warn():
    result = run(HERE, "app.py", env={"LOANS_LOG_LEVEL": "warn"})
    print(f"[1] LOANS_LOG_LEVEL=warn -> exit {result.returncode}: {result.stderr.strip()}")


def try_2_show_secret_in_repr():
    remove_scratch()
    shutil.copytree(HERE, WORK, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns(".tryit-work", "__pycache__", "try_it.py"))
    config = WORK / "config.py"
    config.write_text(config.read_text(encoding="utf-8").replace("repr=False", "repr=True"), encoding="utf-8")
    result = run(WORK, "app.py", env={"LOANS_SMTP_PASSWORD": "example-only"})
    print(f"[2] repr=True -> {result.stdout.splitlines()[0]}")
    tests = run(WORK, "-m", "unittest")
    print(f"[2] python -m unittest -> exit {tests.returncode}; {tests.stderr.strip().splitlines()[-1]}")
    for line in tests.stderr.splitlines():
        if line.startswith("FAIL:"):
            print("    " + line)


if __name__ == "__main__":
    try:
        try_1_lowercase_warn()
        try_2_show_secret_in_repr()
    finally:
        remove_scratch()
