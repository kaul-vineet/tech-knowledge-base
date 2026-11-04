"""Try it: two small experiments on hashing and HMAC (run: python try_it.py)."""
import tempfile
from pathlib import Path

import hash_and_hmac as lab

# 1) Streaming: the chunk size must not change the digest.
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "f.bin"
    p.write_bytes(b"A" * 1_000_000)
    sizes = [7, 4096, 64 * 1024]
    digests = {lab.sha256_file(p, chunk_size=n) for n in sizes}
    print("1) chunk sizes", sizes, "-> distinct digests:", len(digests), "| digest:", digests.pop()[:16] + "...")

# 2) HMAC key sensitivity: change one letter of the RFC 4231 key ("Jefe" -> "jefe").
msg = b"what do ya want for nothing?"
t1, t2 = lab.hmac_sha256(b"Jefe", msg), lab.hmac_sha256(b"jefe", msg)
bits = bin(int(t1, 16) ^ int(t2, 16)).count("1")
print("2) jefe tag:", t2[:16] + "...", "| verifies against Jefe tag:", lab.verify_hmac(b"jefe", msg, t1),
      "| bits differing:", bits, "of 256")
