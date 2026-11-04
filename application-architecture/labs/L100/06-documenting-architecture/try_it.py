"""Try it (lesson 6): edit copies of the docs and re-run the lint. Run: python try_it.py"""
import contextlib
import io
import pathlib
import shutil
import time

from check_docs import DOCS, main

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / ".tryit-work"


def remove_scratch():
    for _ in range(5):  # retry: some network mounts need a second pass
        shutil.rmtree(WORK, ignore_errors=True)
        if not WORK.exists():
            return
        time.sleep(0.5)


def lint_copy(filename, old, new):
    remove_scratch()
    shutil.copytree(DOCS, WORK, copy_function=shutil.copyfile)
    path = WORK / filename
    path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = main(WORK)
    lines = [line for line in out.getvalue().splitlines() if not line.startswith("OK")]
    return code, lines or ["(all OK)"]


def try_1_adr_status():
    for status in ("Reversed.", "Superseded by ADR 2."):
        code, lines = lint_copy("adr-001-sqlite-behind-repository.md", "Accepted.", status)
        print(f"[1] ADR status '{status}' -> exit {code}: " + " | ".join(line.strip() for line in lines))


def try_2_dsl_undefined_container():
    code, lines = lint_copy("workspace.dsl", '        email -> member', '        api -> cache "Caches loans in"\n        email -> member')
    print(f"[2] DSL 'api -> cache' -> exit {code}: " + " | ".join(line.strip() for line in lines))


if __name__ == "__main__":
    try:
        try_1_adr_status()
        try_2_dsl_undefined_container()
    finally:
        remove_scratch()
