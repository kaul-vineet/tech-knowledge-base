"""Try it (lesson 1): two small experiments, run on a scratch copy. Run: python try_it.py"""
import contextlib
import io
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


def scratch_copy():
    remove_scratch()
    shutil.copytree(HERE, WORK, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns(".tryit-work", "__pycache__", "try_it.py"))
    return WORK


def last_line(text):
    return (text.strip().splitlines() or ["(no output)"])[-1]


def try_1_rename_test_file():
    work = scratch_copy()
    (work / "checks_env_test.py").write_text((work / "test_check_env.py").read_text(encoding="utf-8"), encoding="utf-8")
    (work / "test_check_env.py").unlink()
    run = subprocess.run([sys.executable, "-m", "unittest"], cwd=work, capture_output=True, text=True, encoding="utf-8")
    print(f"[1] test file renamed to checks_env_test.py -> exit {run.returncode}: {last_line(run.stderr)}")


def try_2_raise_min_python():
    import check_env
    check_env.MIN_PYTHON = (3, 99)  # pretend the labs need a Python that does not exist yet
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = check_env.main()
    print(f"[2] MIN_PYTHON=(3, 99) -> main() returns {code}; python line: {out.getvalue().splitlines()[1]}")


if __name__ == "__main__":
    try:
        try_1_rename_test_file()
        try_2_raise_min_python()
    finally:
        remove_scratch()
