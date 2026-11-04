"""Evidence for the decision: pairwise fan-out vs sender keys vs an MLS-style tree, for groups of 8, 64 and 256.
Counts are public-key (HPKE) or AEAD encryptions the SENDING side performs. Pairwise and sender keys run real HPKE for
n <= 64 and count only above that (same code path, crypto switched off); the tree always runs for real."""
import json
import os
import time

from cryptography.hazmat.primitives.asymmetric import x25519

import group_keys as gk
import solution_remove

SECRET = os.urandom(32)


def hpke_to(pub, crypto: bool) -> int:
    return len(gk.SUITE.encrypt(SECRET, pub, info=b"kb-l20 compare")) if crypto else 80  # 32 enc + 32 + 16 tag


def pairwise(n: int, crypto: bool) -> dict:
    """No group key: every message is encrypted once per recipient; removing someone = stop sending to them."""
    keys = [gk.AESGCM(gk.AESGCM.generate_key(bit_length=128)) for _ in range(n - 1)]  # one pairwise key per peer
    sent = [k.encrypt(os.urandom(12), b"hello group", None) if crypto else None for k in keys]
    return {"design": "pairwise", "n": n, "encryptions_per_message": len(sent), "encryptions_per_removal": 0,
            "bytes_per_removal": 0}


def sender_keys(n: int, crypto: bool) -> dict:
    """Each member has a sender chain key, given to every other member over pairwise channels (HPKE here).
    After a removal every remaining member must make a NEW sender key and send it to every other remaining member."""
    pubs = [x25519.X25519PrivateKey.generate().public_key() for _ in range(n)] if crypto else [None] * n
    count = size = 0
    for sender in range(n - 1):  # members 0 .. n-2 remain, member n-1 was removed
        for receiver in range(n - 1):
            if receiver != sender:
                size += hpke_to(pubs[receiver], crypto)
                count += 1
    return {"design": "sender keys", "n": n, "encryptions_per_message": 1, "encryptions_per_removal": count,
            "bytes_per_removal": size}


def mls_tree(n: int) -> dict:
    g = solution_remove.Group([f"m{i}" for i in range(n)])
    t = time.perf_counter()
    sent = g.commit("m0", remove=f"m{n - 1}")
    ms = round((time.perf_counter() - t) * 1000, 1)
    msg = g.send("m0", "after removal")
    return {"design": "MLS-style tree (toy)", "n": n, "encryptions_per_message": 1, "encryptions_per_removal": sent,
            "bytes_per_removal": sent * 80, "removed_can_read": g.read(f"m{n - 1}", msg) is not None,
            "commit_and_process_ms": ms}


if __name__ == "__main__":
    for n in (8, 64, 256):
        crypto = n <= 64
        for row in (pairwise(n, crypto), sender_keys(n, crypto), mls_tree(n)):
            print(json.dumps({**row, "real_crypto": crypto or row["design"].startswith("MLS")}))  # else: counted only
