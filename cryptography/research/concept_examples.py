"""Computes every number used in the worked examples of content/concepts/*.md and the primer.

Run: python research/concept_examples.py  (output saved to research/concept_examples.out.txt)
"""
import base64
import hashlib
import hmac
import math
import random
import time

import cryptography
from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


def bits_differ(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


print("== 01 setup: two layers, one answer")
print("cryptography", cryptography.__version__, "|", backend.openssl_version_text())
h = hashes.Hash(hashes.SHA256())
h.update(b"abc")
pyca = h.finalize().hex()
std = hashlib.sha256(b"abc").hexdigest()
print("pyca  SHA256(abc)", pyca)
print("stdlib SHA256(abc)", std, "equal:", pyca == std)

print("\n== 02 hashing: avalanche + HMAC")
d1, d2 = hashlib.sha256(b"abc").digest(), hashlib.sha256(b"abd").digest()
print("SHA256(abd)", d2.hex())
print("bits that differ out of 256:", bits_differ(d1, d2))
print("HMAC-SHA256(Jefe, 'what do ya want for nothing?')",
      hmac.new(b"Jefe", b"what do ya want for nothing?", hashlib.sha256).hexdigest())
print("plain SHA256('what do ya want for nothing?')",
      hashlib.sha256(b"what do ya want for nothing?").hexdigest())

print("\n== 03 randomness: seeds and entropy")
r1, r2 = random.Random(42), random.Random(42)
a = [r1.getrandbits(32) for _ in range(3)]
b = [r2.getrandbits(32) for _ in range(3)]
print("Random(42) first 3 outputs:", a, "| second generator same:", a == b)
print("seeds in +/-1h window:", 7201, "~ 2^%.1f" % math.log2(7201))
print("6-digit PIN space: 10^6 ~ 2^%.2f bits" % math.log2(10**6))
print("32-byte token: 256 bits; token_urlsafe(32) length:", len(base64.urlsafe_b64encode(bytes(32)).rstrip(b"=")))

print("\n== 04 AEAD: sizes and nonce reuse")
v_key = bytes(range(0x80, 0xA0))
v_nonce = bytes.fromhex("070000004041424344454647")
v_aad = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
v_pt = (b"Ladies and Gentlemen of the class of '99: If I could offer you only one tip "
        b"for the future, sunscreen would be it.")
out = ChaCha20Poly1305(v_key).encrypt(v_nonce, v_pt, v_aad)
print("RFC 8439 plaintext bytes:", len(v_pt), "output bytes:", len(out), "tag:", out[-16:].hex())
p1, p2 = b"attack at dawn!!", b"retreat at dusk!"
k, n = bytes(32), bytes(12)  # fixed all-zero key/nonce so the example is reproducible
c1 = AESGCM(k).encrypt(n, p1, None)[:16]
c2 = AESGCM(k).encrypt(n, p2, None)[:16]
x = bytes(i ^ j for i, j in zip(c1, c2))
print("c1 xor c2:", x.hex())
print("p1 xor p2:", bytes(i ^ j for i, j in zip(p1, p2)).hex(), "equal:", x == bytes(i ^ j for i, j in zip(p1, p2)))
print("recovered p2 from p1:", bytes(i ^ j for i, j in zip(x, p1)))

print("\n== 05 passwords: cost and salts")
salt_a, salt_b = b"A" * 16, b"B" * 16
phc_a = Argon2id(salt=salt_a, length=32, iterations=2, lanes=1, memory_cost=19456).derive_phc_encoded(b"hunter2")
phc_b = Argon2id(salt=salt_b, length=32, iterations=2, lanes=1, memory_cost=19456).derive_phc_encoded(b"hunter2")
print("PHC salt A:", phc_a)
print("PHC salt B:", phc_b)
print("19456 KiB =", 19456 / 1024, "MiB")
t = time.perf_counter()
N = 200_000
for i in range(N):
    hashlib.sha256(b"password%d" % i).digest()
sha_rate = N / (time.perf_counter() - t)
t = time.perf_counter()
M = 10
for i in range(M):
    Argon2id(salt=salt_a, length=32, iterations=2, lanes=1, memory_cost=19456).derive(b"pw%d" % i)
argon_rate = M / (time.perf_counter() - t)
print("SHA-256 guesses/s (1 core, sandbox): %.0f" % sha_rate)
print("Argon2id m=19MiB,t=2,p=1 guesses/s (1 core, sandbox): %.1f" % argon_rate)
print("slow-down factor: ~%.0fx" % (sha_rate / argon_rate))

print("\n== 06 encoding")
print("base64('Aladdin:open sesame'):", base64.b64encode(b"Aladdin:open sesame").decode())
print("decode back:", base64.b64decode("QWxhZGRpbjpvcGVuIHNlc2FtZQ==").decode())
print("hex('Hi'):", b"Hi".hex(), "| base64('Hi'):", base64.b64encode(b"Hi").decode())
print("size 30 bytes -> base64", len(base64.b64encode(bytes(30))), "chars, hex", len(bytes(30).hex()), "chars")
