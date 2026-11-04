"""Library Loans' borrow path: members must answer; the catalogue title is nice to have (fallback allowed).

Base wiring: ONE shared pool for every outbound call - the weakness the failureLab exposes.
"""
from resilience import CircuitBreaker, Pool, json_log, with_fallback

TIMEOUT_S = 0.1
FALLBACK_TITLE = "(title unavailable)"


class LoanService:
    def __init__(self, members, catalogue, members_pool, catalogue_pool, breaker):
        self.members, self.catalogue, self.breaker = members, catalogue, breaker
        self.members_pool, self.catalogue_pool = members_pool, catalogue_pool

    def borrow(self, member_id, book_id):
        if not self.members_pool.call(self.members.check, member_id, timeout=TIMEOUT_S):  # required: no fallback
            raise PermissionError(f"{member_id} may not borrow")
        title, degraded = with_fallback(
            lambda: self.breaker.call(self.catalogue_pool.call, self.catalogue.title, book_id, timeout=TIMEOUT_S),
            lambda exc: FALLBACK_TITLE)
        return {"member": member_id, "book": book_id, "title": title, "degraded": degraded}

    def pools(self):
        return {pool.name: f"{pool.busy}/{pool.workers}" for pool in {self.members_pool, self.catalogue_pool}}

    def close(self):
        for pool in {self.members_pool, self.catalogue_pool}:
            pool.shutdown()


def build_service(members, catalogue, log=json_log):
    shared = Pool("shared", 8)  # one pool for every dependency: a slow one can take all 8 threads
    return LoanService(members, catalogue, shared, shared, CircuitBreaker("catalogue", open_s=0.3, log=log))
