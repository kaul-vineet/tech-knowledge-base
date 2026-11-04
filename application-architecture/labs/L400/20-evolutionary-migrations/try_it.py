"""Try it (lesson 20): keep the old column NOT NULL; let the release flag outlive its expiry date.

Run: python try_it.py   (scratch copy in .tryit-work/, deleted after)
"""
import shutil
import time
from datetime import date

import rollout
from app import HERE, load
from flags import Flags, gate_flags

WORK = HERE / ".tryit-work"


def try_1_old_column_not_null():
    WORK.mkdir(exist_ok=True)
    text = (HERE / "solution" / "migrations.py").read_text(encoding="utf-8")
    (WORK / "migrations.py").write_text(text.replace("name TEXT)", "name TEXT NOT NULL)"), encoding="utf-8")
    r, rows = rollout.expand_contract(load(WORK / "migrations.py", "migrations_not_null"))
    errors = {row["step"].split(":")[0]: row["errors"] for row in rows if row["errors"]}
    print(f"[1] name TEXT NOT NULL -> {r.errors} failed requests {errors}; first: {r.log[0]}")


def try_2_flag_outlives_expiry():
    later = Flags(today=date(2026, 12, 1))
    print(f"[2] today 2026-12-01 -> {gate_flags(later)}")


if __name__ == "__main__":
    try:
        try_1_old_column_not_null()
        try_2_flag_outlives_expiry()
    finally:
        for _ in range(5):  # retry: some network mounts need a second pass
            shutil.rmtree(WORK, ignore_errors=True)
            if not WORK.exists():
                break
            time.sleep(0.5)
