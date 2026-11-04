"""Lesson 18 failureLab: a new overdue report forgets the tenant filter. Shared schema, 50 libraries.

Run: python failure_lab.py
"""
import pathlib
import shutil
import tempfile

import fitness_tenant
import tenancy
from app import HERE, TENANTS, use_repository


def main():
    for label, path in [("base    ", HERE / "repository.py"), ("solution", HERE / "solution" / "repository.py")]:
        use_repository(path)
        work = pathlib.Path(tempfile.mkdtemp(prefix=".work-", dir=HERE))
        try:
            layout = tenancy.SharedSchema(work)
            tenancy.seed(layout, TENANTS)
            s = layout.session("lib00")
            with tenancy.TenantGuard(s) as guard:
                rows = tenancy.repository.overdue(s, "2026-10-28")
            s.conn.close()
        finally:
            shutil.rmtree(work, ignore_errors=True)
        gate = fitness_tenant.gate([path])
        print(f"{label}: lib00 overdue report returns {len(rows)} rows, {sum(not r[1].startswith('lib00') for r in rows)} "
              f"from other libraries; guard violations {len(guard.violations)}; static gate ok={gate['ok']}")
        if guard.violations:
            print(f"    guard saw: {guard.violations[0]}")


if __name__ == "__main__":
    main()
