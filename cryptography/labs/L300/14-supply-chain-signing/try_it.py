"""Try it: signer key rotation and a one-byte manifest change (run: python try_it.py)."""
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import release_sign as rs
from solution_strict import install

old, new = (Ed25519PrivateKey.from_private_bytes(bytes([n]) * 32) for n in (1, 2))  # DEMO keys: fixed kids
ring = {rs.key_id(k.public_key()): k.public_key() for k in (old, new)}  # rotation window: both kids trusted

with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as out:
    v1, v2 = Path(a), Path(b)
    for dist, key, ver in ((v1, old, "1.0.0"), (v2, new, "2.0.0")):
        rs.build_artifacts(dist)
        rs.sign_release(dist, key, ver)
    # 1) During rotation both releases install; after the old kid is removed, the 1.0.0 release no longer does.
    for label, trusted in (("both keys trusted", ring), ("old key removed", {rs.key_id(new.public_key()): new.public_key()})):
        res = []
        for dist in (v1, v2):
            try:
                res.append(f"{len(install(dist, Path(out), trusted))} files")
            except rs.Rejected as e:
                res.append(f"REJECTED ({e})")
        print(f"1) {label:<18} v1.0.0: {res[0]:<40} v2.0.0: {res[1]}")
    # 2) Change one digest character inside the signed manifest (an attacker "fixing" the hash).
    raw = (v2 / "MANIFEST.json").read_bytes()
    i = raw.index(b'"sha256": "') + 11
    (v2 / "MANIFEST.json").write_bytes(raw[:i] + (b"0" if raw[i:i + 1] != b"0" else b"1") + raw[i + 1:])
    try:
        install(v2, Path(out), ring)
    except rs.Rejected as e:
        print("2) one hex digit changed in MANIFEST.json:", e)
