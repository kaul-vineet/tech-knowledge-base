"""A minimal transparency log in the RFC 9162 style: append-only list of JCS entries, Merkle tree head signed by the
log key (STH), inclusion proofs (this release is in the log) and consistency proofs (the log only grew).
One log, no gossip between clients: split-view detection needs monitors/witnesses (RFC 9162 section 11.3)."""
import canonical as C
import merkle
import trust


def entry(name: str, version: int, release_sha256: str) -> bytes:
    return C.dumps({"name": name, "release_sha256": release_sha256, "version": version})


class Log:
    def __init__(self, signer: trust.Signer):
        self.signer, self.entries = signer, []

    def add(self, e: bytes) -> int:
        self.entries.append(e)
        return len(self.entries) - 1

    def sth(self, now: int) -> dict:
        root = merkle.mth(self.entries).hex()
        return trust.sign({"_type": "sth", "size": len(self.entries), "root": root, "timestamp": now}, [self.signer])

    def inclusion(self, index: int, size: int) -> list:
        return [h.hex() for h in merkle.inclusion_proof(index, self.entries[:size])]

    def consistency(self, old: int, new: int) -> list:
        return [h.hex() for h in merkle.consistency_proof(old, self.entries[:new])]

    def index_of(self, e: bytes) -> int:
        return self.entries.index(e)
