"""Library Loans, production-shaped (capstone core). Every request: policy -> tenant-scoped SQL -> outbox.

PEP     each public method calls self._authorize() first (lesson 19 policy, decision log, email erased)
tenancy shared schema; every statement carries the tenant id; TenantGuard checks it at runtime (lesson 18)
fines   through the strangler facade (lesson 17): shadow until the cut-over criteria pass, then the service
events  loan row + outbox row in ONE transaction; a relay publishes them at least once (lesson 9)
SLIs    one JSON line per request (route, status, ms) for the lesson 15 SLO maths
"""
import json
import sqlite3
import time

from reuse import events, tenancy

SCHEMA = """
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, tenant_id TEXT NOT NULL, member_id TEXT NOT NULL,
    member_type TEXT NOT NULL, book_id TEXT NOT NULL, returned INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS loans_tenant ON loans (tenant_id, member_id);
CREATE TABLE IF NOT EXISTS outbox (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL,
    channel TEXT NOT NULL, payload TEXT NOT NULL, published_at TEXT);
"""
ACTIVE = "SELECT COUNT(*) FROM loans WHERE tenant_id = :tenant AND member_id = :member AND returned = 0"
INSERT_LOAN = "INSERT INTO loans (tenant_id, member_id, member_type, book_id) VALUES (:tenant, :member, :kind, :book)"
FIND_LOAN = "SELECT member_id, member_type, book_id FROM loans WHERE tenant_id = :tenant AND id = :loan AND returned = 0"
RETURN_LOAN = "UPDATE loans SET returned = 1 WHERE tenant_id = :tenant AND id = :loan"
MEMBER_LOANS = \
    "SELECT id, book_id FROM loans WHERE tenant_id = :tenant AND member_id = :member AND returned = 0 ORDER BY id"
OUTBOX = "INSERT INTO outbox (tenant_id, channel, payload) VALUES (:tenant, :channel, :payload)"


class Forbidden(Exception):
    pass


class LoansService:
    def __init__(self, pdp, fines, db_path=":memory:", clock=None):
        self.pdp, self.fines = pdp, fines
        self.db = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        self.db.executescript(SCHEMA)  # named parameters: every statement binds :tenant
        self.clock = clock or (lambda: "2026-10-28T09:00:00Z")
        self.request_log, self.guard_violations = [], []

    def _authorize(self, action, subject, tenant, member_id, **extra):
        resource = {"tenant": tenant, "member_id": member_id, **extra}
        if not self.pdp.decide({"action": action, "subject": subject, "resource": resource})["allowed"]:
            raise Forbidden(f"{action} denied for {subject.get('id')} in {tenant}")

    def _scoped(self, tenant):
        """A tenant session on the shared connection; TenantGuard records any statement without this tenant."""
        guard = tenancy.TenantGuard(tenancy.Session(self.db, "loans", tenant))
        return guard

    def _timed(self, route, fn):
        start, status = time.perf_counter(), 200
        try:
            return fn()
        except Forbidden:
            status = 403
            raise
        except Exception:
            status = 500
            if self.db.in_transaction:
                self.db.execute("ROLLBACK")
            raise
        finally:  # one JSON line per request: the SLI source
            self.request_log.append(json.dumps({"ts": self.clock(), "route": route, "status": status,
                                                "ms": round((time.perf_counter() - start) * 1000, 2)}))

    def borrow(self, subject, tenant, member_id, member_type, book_id):
        def work():
            with self._scoped(tenant) as guard:
                active = self.db.execute(ACTIVE, {"tenant": tenant, "member": member_id}).fetchone()[0]  # trusted attribute
                self._authorize("borrow", subject, tenant, member_id, active_loans=active)
                self.db.execute("BEGIN")  # loan + event: both or neither
                loan_id = self.db.execute(INSERT_LOAN, {"tenant": tenant, "member": member_id, "kind": member_type,
                                                       "book": book_id}).lastrowid
                self._event(tenant, "LoanCreated", {"loanId": loan_id, "memberId": member_id, "bookId": book_id})
                self.db.execute("COMMIT")
            self.guard_violations += guard.violations
            return loan_id
        return self._timed("POST /loans", work)

    def give_back(self, subject, tenant, loan_id, days_late):
        def work():
            with self._scoped(tenant) as guard:
                member_id, member_type, book_id = self.db.execute(FIND_LOAN, {"tenant": tenant, "loan": loan_id}).fetchone()
                self._authorize("return", subject, tenant, member_id)
                fine = self.fines.fine(member_id, days_late, member_type)  # strangler facade decides the route
                self.db.execute("BEGIN")
                self.db.execute(RETURN_LOAN, {"tenant": tenant, "loan": loan_id})
                self._event(tenant, "LoanReturned", {"loanId": loan_id, "memberId": member_id, "bookId": book_id,
                                                     "fine": fine})
                self.db.execute("COMMIT")
            self.guard_violations += guard.violations
            return fine
        return self._timed("POST /returns", work)

    def loans_of(self, subject, tenant, member_id):
        def work():
            self._authorize("view", subject, tenant, member_id)
            with self._scoped(tenant) as guard:
                rows = self.db.execute(MEMBER_LOANS, {"tenant": tenant, "member": member_id}).fetchall()
            self.guard_violations += guard.violations
            return [{"loanId": i, "bookId": b} for i, b in rows]
        return self._timed("GET /loans", work)

    def _event(self, tenant, event_type, data):
        event = events.new_event(event_type, {"tenant": tenant, **data}, occurred_at=self.clock(),
                                 event_id=f"{tenant}-{event_type}-{data['loanId']}")  # stable id: dedupe key
        self.db.execute(OUTBOX, {"tenant": tenant, "channel": events.CHANNEL[event_type], "payload": json.dumps(event)})
