"""Nonce-reuse detection: an in-process tripwire plus an offline scan of stored ciphertexts.
Fault: a nonce generator seeded with a constant restarts at the same sequence after every process restart."""
import hashlib
import os
import random

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class NonceReuseError(Exception):
    pass


class GuardedAESGCM:
    """Refuses a second encryption with the same nonce under this key, in THIS process only."""

    def __init__(self, key: bytes):
        self.aead, self.seen = AESGCM(key), set()

    def seal(self, nonce: bytes, data: bytes) -> bytes:
        if nonce in self.seen:
            raise NonceReuseError(f"nonce {nonce.hex()} reused")
        self.seen.add(nonce)
        return nonce + self.aead.encrypt(nonce, data, None)


def buggy_nonces(seed=15):
    rng = random.Random(seed)  # BUG: predictable PRNG with a fixed seed -> same nonces after a restart
    while True:
        yield rng.randbytes(12)


def good_nonces():
    while True:
        yield os.urandom(12)  # 96-bit random nonces: fine for well under 2**32 messages per key


def scan_for_reuse(blobs) -> dict:
    """Offline audit: nonce -> indexes of stored blobs that share it. Works across restarts and hosts."""
    seen = {}
    for i, blob in enumerate(blobs):
        seen.setdefault(blob[:12], []).append(i)
    return {n.hex(): idx for n, idx in seen.items() if len(idx) > 1}


def two_restarts(nonce_source, key, runs):
    stored = []
    for messages in runs:  # each run = one process lifetime: a fresh guard and a fresh nonce generator
        guard, nonces = GuardedAESGCM(key), nonce_source()
        stored += [guard.seal(next(nonces), m) for m in messages]
    return stored


if __name__ == "__main__":
    key = hashlib.sha256(b"demo key - never derive real keys like this").digest()
    runs = [[b"pay alice 10", b"pay bob 20  "], [b"pay mal 9999", b"pay eve 7777"]]
    guard, n = GuardedAESGCM(key), os.urandom(12)
    guard.seal(n, b"first")
    try:
        guard.seal(n, b"second")
    except NonceReuseError:
        print("in-process tripwire: NonceReuseError on the 2nd seal with the same nonce")
    for name, src in (("buggy seeded nonces", buggy_nonces), ("os.urandom nonces", good_nonces)):
        dup = scan_for_reuse(two_restarts(src, key, runs))
        print(f"{name:<20} 2 restarts x 2 messages: tripwire silent, offline scan finds {len(dup)} reused {list(dup.values())}")
    blobs = two_restarts(buggy_nonces, key, runs)
    leak = bytes(x ^ y for x, y in zip(blobs[0][12:24], blobs[2][12:24]))  # same key+nonce: ct XOR = pt XOR
    print("attacker knows run-1 message 0, recovers run-2 message 0:", bytes(x ^ y for x, y in zip(leak, runs[0][0])))
