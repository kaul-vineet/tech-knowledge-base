"""Three multi-tenancy layouts for Library Loans on SQLite files, measured side by side (lesson 18 lab code).

shared-schema      one file, one loans table, a tenant_id column on every row (isolation = a WHERE clause)
schema-per-tenant  one file, one loans table per tenant (SQLite has no CREATE SCHEMA: table name = namespace)
db-per-tenant      one SQLite file per tenant (isolation = the connection)
TenantGuard checks at runtime that every statement on a tenant table names the CURRENT tenant id.
Run the comparison: python app.py
"""
import re
import sqlite3
from datetime import date, timedelta

import repository

COLUMNS = "id INTEGER PRIMARY KEY, tenant_id TEXT NOT NULL, member_id TEXT NOT NULL, book_id TEXT NOT NULL, due TEXT"


class Session:
    """What a request gets: a connection, the table to use and the tenant it acts for."""

    def __init__(self, conn, table, tenant):
        self.conn, self.table, self.tenant = conn, table, tenant


class SharedSchema:
    kind = "shared-schema"

    def __init__(self, folder):
        self.path = folder / "shared.sqlite"

    def session(self, tenant, timeout=5.0):
        conn = sqlite3.connect(self.path, isolation_level=None, timeout=timeout)
        conn.execute(f"CREATE TABLE IF NOT EXISTS loans ({COLUMNS})")
        conn.execute("CREATE INDEX IF NOT EXISTS loans_tenant ON loans (tenant_id, member_id)")  # tenant first
        return Session(conn, "loans", tenant)

    def files(self, tenants):
        return 1

    def tables(self, tenants):
        return [("main", "loans")]


class SchemaPerTenant(SharedSchema):
    kind = "schema-per-tenant"

    def session(self, tenant, timeout=5.0):
        conn = sqlite3.connect(self.path, isolation_level=None, timeout=timeout)
        conn.execute(f"CREATE TABLE IF NOT EXISTS loans__{tenant} ({COLUMNS})")
        return Session(conn, f"loans__{tenant}", tenant)

    def tables(self, tenants):
        return [("main", f"loans__{t}") for t in tenants]


class DbPerTenant:
    kind = "db-per-tenant"

    def __init__(self, folder):
        self.folder = folder / "tenants"
        self.folder.mkdir(exist_ok=True)

    def session(self, tenant, timeout=5.0):
        conn = sqlite3.connect(self.folder / f"{tenant}.sqlite", isolation_level=None, timeout=timeout)
        conn.execute(f"CREATE TABLE IF NOT EXISTS loans ({COLUMNS})")
        return Session(conn, "loans", tenant)

    def files(self, tenants):
        return len(tenants)

    def tables(self, tenants):
        return [(t, "loans") for t in tenants]


LAYOUTS = [SharedSchema, SchemaPerTenant, DbPerTenant]
TENANT_TABLE = re.compile(r"\b(FROM|UPDATE|INTO|JOIN)\s+(loans\w*)", re.I)


class TenantGuard:
    """Runtime tenant scoping: the trace callback sees each statement with its bound values (expanded SQL)."""

    def __init__(self, session):
        self.session, self.violations = session, []

    def __enter__(self):
        self.session.conn.set_trace_callback(self.check)
        return self

    def __exit__(self, *exc):
        self.session.conn.set_trace_callback(None)

    def check(self, sql):
        if not TENANT_TABLE.search(sql) or sql.lstrip().upper().startswith(("CREATE", "BEGIN", "COMMIT")):
            return
        if f"'{self.session.tenant}'" not in sql:  # every tenant-table statement must carry THIS tenant's id
            self.violations.append(sql)


def seed(layout, tenants, loans_per_tenant=40, today=date(2026, 10, 28)):
    for t_index, tenant in enumerate(tenants):
        s = layout.session(tenant)
        s.conn.execute("BEGIN")
        for i in range(loans_per_tenant):  # every 3rd loan is overdue: due 1-5 days before today
            due = today - timedelta(days=1 + i % 5) if i % 3 == 0 else today + timedelta(days=7 + i % 14)
            repository.borrow(s, f"{tenant}-m{i % 12}", f"b{t_index}-{i}", due.isoformat())
        s.conn.execute("COMMIT")
        s.conn.close()


def leak_check(layout, tenant, today="2026-10-28"):
    """Isolation: rows from OTHER tenants returned by the overdue report, plus the guard's verdict."""
    s = layout.session(tenant)
    with TenantGuard(s) as guard:
        rows = repository.overdue(s, today)
    s.conn.close()
    return {"rows": len(rows), "leaked": sum(r[1].split("-")[0] != tenant for r in rows),
            "guard_violations": len(guard.violations)}


def noisy_neighbour(layout, busy_tenant, victim, attempts=20):
    """Tenant A holds a write transaction (bulk import); tenant B tries to borrow with no lock wait."""
    a = layout.session(busy_tenant)
    a.conn.execute("BEGIN IMMEDIATE")  # SQLite: one writer per FILE
    for i in range(500):
        repository.borrow(a, f"{busy_tenant}-bulk", f"bulk-{i}", "2026-12-01")
    b, blocked = layout.session(victim, timeout=0), 0
    for i in range(attempts):
        try:
            repository.borrow(b, f"{victim}-m1", f"new-{i}", "2026-11-11")
        except sqlite3.OperationalError:  # "database is locked": the neighbour's import blocks us
            blocked += 1
    a.conn.execute("ROLLBACK")
    a.conn.close()
    b.conn.close()
    return {"attempts": attempts, "blocked": blocked}


def migrate(layout, tenants, ddl="ALTER TABLE {db}.{table} ADD COLUMN renewals INTEGER NOT NULL DEFAULT 0"):
    """Migration effort: DDL statements to run and files to touch for ONE schema change."""
    statements = 0
    for db, table in layout.tables(tenants):
        s = layout.session(db if db != "main" else tenants[0])
        s.conn.execute(ddl.format(db="main", table=table))
        s.conn.close()
        statements += 1
    return {"ddl_statements": statements, "files": layout.files(tenants)}
