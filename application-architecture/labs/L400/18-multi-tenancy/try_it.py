"""Try it (lesson 18): ATTACH one SQLite file per tenant into one connection; scope a query to the wrong tenant.

Run: python try_it.py   (scratch files in .tryit-work/, deleted after)
"""
import shutil
import sqlite3
import time

import tenancy
from app import HERE, use_repository

WORK = HERE / ".tryit-work"


def try_1_attach_limit():
    WORK.mkdir(exist_ok=True)
    conn, attached = sqlite3.connect(":memory:"), 0
    try:
        for i in range(12):  # "schema per tenant" via ATTACH: one schema name per tenant file
            conn.execute(f"ATTACH DATABASE ? AS lib{i:02d}", (str(WORK / f"lib{i:02d}.sqlite"),))
            attached += 1
    except sqlite3.OperationalError as exc:
        print(f"[1] attached {attached} tenant files, then: {exc}")
    conn.close()


def try_2_wrong_tenant_id():
    use_repository(HERE / "solution" / "repository.py")
    layout = tenancy.SharedSchema(WORK)
    tenancy.seed(layout, ["lib00", "lib01"], loans_per_tenant=6)
    s = layout.session("lib00")
    with tenancy.TenantGuard(s) as guard:
        rows = s.conn.execute("SELECT id FROM loans WHERE tenant_id = ?", ("lib01",)).fetchall()  # hard-coded id
    s.conn.close()
    print(f"[2] session lib00 queries tenant_id='lib01' -> {len(rows)} rows; guard violations {guard.violations}")


if __name__ == "__main__":
    try:
        try_1_attach_limit()
        try_2_wrong_tenant_id()
    finally:
        for _ in range(5):  # retry: some network mounts need a second pass
            shutil.rmtree(WORK, ignore_errors=True)
            if not WORK.exists():
                break
            time.sleep(0.5)
