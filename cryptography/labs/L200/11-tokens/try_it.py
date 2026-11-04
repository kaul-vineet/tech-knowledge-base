"""Try it: two experiments on signed tokens (run: python try_it.py)."""
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import tokens as lab

sk, now = Ed25519PrivateKey.generate(), 1_800_000_000
keys = {"EdDSA": sk.public_key()}

# 1) A token that expired 20 s ago: accepted with the default 30 s leeway, rejected with leeway=0.
tok = lab.sign({"aud": "orders-api", "exp": now - 20}, "EdDSA", sk)
for leeway in (30, 0):
    try:
        lab.verify(tok, keys, "orders-api", now=now, leeway=leeway)
        print(f"1) expired 20 s ago, leeway={leeway:>2}: accepted")
    except lab.TokenError as e:
        print(f"1) expired 20 s ago, leeway={leeway:>2}: rejected ({e})")

# 2) Signed is not encrypted: anyone can read the claims without any key.
tok = lab.sign({"sub": "alice", "email": "alice@example.com", "aud": "orders-api", "exp": now + 60}, "EdDSA", sk)
print("2) payload read with NO key:", json.loads(lab.unb64u(tok.split(".")[1])))
