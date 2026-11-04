"""Build-task reference: nonce = Raft term (4 bytes) || counter within that term (8 bytes), big-endian.
Unique per epoch key because (1) only the leader seals, (2) Raft elects at most one leader per term (Election
Safety) and (3) the term is persistent, replicated state: a new or restarted leader is always in a NEWER term, so
it can never re-enter an old (term, counter) range even though its counter restarts at 1."""


class DerivedNonce:
    def __init__(self):
        self.term, self.counter = None, 0

    def next(self, term: int) -> bytes:
        if self.term is not None and term < self.term:
            raise ValueError(f"term went backwards ({term} < {self.term}): a deposed sealer must not seal")
        if term != self.term:
            self.term, self.counter = term, 0  # new term: the 4-byte prefix alone makes the range fresh
        if term >= 2**32 or self.counter >= 2**64 - 1:
            raise OverflowError("nonce space exhausted: rotate the epoch key")
        self.counter += 1
        return term.to_bytes(4, "big") + self.counter.to_bytes(8, "big")
