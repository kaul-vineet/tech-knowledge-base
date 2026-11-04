"""Loans repository used by every tenancy layout. Every statement on loans must be scoped by tenant_id.

Solution: the overdue report filters by tenant_id like every other statement (bound parameter, first condition).
"""
BORROW = "INSERT INTO {table} (tenant_id, member_id, book_id, due) VALUES (?, ?, ?, ?)"
MEMBER_LOANS = "SELECT id, member_id, book_id, due FROM {table} WHERE tenant_id = ? AND member_id = ? ORDER BY id"
OVERDUE = "SELECT id, member_id, book_id, due FROM {table} WHERE tenant_id = ? AND due < ? ORDER BY id"


def borrow(session, member_id, book_id, due):
    session.conn.execute(BORROW.format(table=session.table), (session.tenant, member_id, book_id, due))


def member_loans(session, member_id):
    return session.conn.execute(MEMBER_LOANS.format(table=session.table), (session.tenant, member_id)).fetchall()


def overdue(session, today):
    return session.conn.execute(OVERDUE.format(table=session.table), (session.tenant, today)).fetchall()
