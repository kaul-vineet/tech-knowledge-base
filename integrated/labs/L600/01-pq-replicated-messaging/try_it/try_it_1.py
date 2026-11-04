"""tryIt 1: the failure lab's nonce reuse, but with a misuse-resistant AEAD. Same key, same 12-byte nonce, two
different messages: does XOR-ing the ciphertexts with one known plaintext still reveal the other?
AES-GCM is CTR mode underneath (same nonce = same keystream). AES-GCM-SIV (RFC 8452) derives the CTR start from a
tag over the plaintext, so different plaintexts get different keystreams; only an identical (nonce, plaintext)
pair repeats - which leaks equality, nothing more."""
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESGCMSIV

known, secret = b"msg 00000 from alice: status green", b"msg 00010 from bob: status green"
key, nonce = os.urandom(32), (1).to_bytes(12, "big")  # the leader-counter's first nonce, reused after failover
for name, aead in (("AES-256-GCM", AESGCM(key)), ("AES-256-GCM-SIV", AESGCMSIV(key))):
    c1, c2 = aead.encrypt(nonce, known, None), aead.encrypt(nonce, secret, None)
    n = len(secret)
    guess = bytes(a ^ b ^ k for a, b, k in zip(c1[:n], c2[:n], known))
    same = aead.encrypt(nonce, known, None) == c1
    print(f"{name:16} recovered == secret: {guess == secret} | repeat of the same message is identical: {same}")
