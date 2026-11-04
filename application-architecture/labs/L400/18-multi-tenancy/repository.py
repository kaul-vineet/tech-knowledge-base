"""Loans repository used by every tenancy layout. Every statement on loans must be scoped by tenant_id.

The overdue report is NEW code (the failureLab): it forgot the tenant filter. With one shared table that
returns every library's overdue loans; the fitness test (fitness_tenant.py) and TenantGuard both catch it.
"""
BORROW = "INSERT INTO {table} (tenant_id, member_id, book_id, due) VALUES (?, ?, ?, ?)"
MEMBER_LOANS = "SELECT id, member_id, book_id, due FROM {table} WHERE tenant_id = ? AND member_id = ? ORDER BY id"
OVERDUE = "SELECT id, member_id, book_id, due FROM {table} WHERE due < ? ORDER BY id"


def borrow(session, member_id, book_id, due):
    session.conn.execute(BORROW.format(table=session.table), (session.tenant, member_id, book_id, due))


def member_loans(session, member_id):
    return session.conn.execute(MEMBER_LOANS.format(table=session.table), (session.tenant, member_id)).fetchall()


def overdue(session, today):
    return session.conn.execute(OVERDUE.format(table=session.table), (today,)).fetchall()
