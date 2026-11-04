"""Computes the `expected` values of the learningTools exercises (CyberChef, Wireshark, step CLI ...) from the labs' own code.

Run from the cryptography folder: python research/learning_tools_expected.py
(output saved to research/learning_tools_expected.out.txt). The GUI tools themselves were NOT run here.
"""
import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

LABS = Path(__file__).resolve().parent.parent / "labs"
for lab in ("L100/02-hashing-integrity", "L100/04-authenticated-encryption", "L100/05-password-storage",
            "L100/06-encoding-hashing-encryption", "L200/11-tokens"):
    sys.path.insert(0, str(LABS / lab))
import aead_demo  # noqa: E402
import compare  # noqa: E402
import hash_and_hmac  # noqa: E402
import passwords  # noqa: E402
import tool_check  # noqa: E402

print("L2  CyberChef SHA2 (SHA-256) of 'abc':", hash_and_hmac.sha256_text("abc"))
print("L2  CyberChef HMAC SHA256 key 'Jefe':", hash_and_hmac.hmac_sha256(b"Jefe", b"what do ya want for nothing?"))

g = aead_demo.GCM_TC14
print("L4  GCM TC14 decrypt -> plaintext hex:", AESGCM(g["key"]).decrypt(g["nonce"], g["ct"] + g["tag"], None).hex())
bad = bytearray(g["ct"])
bad[0] ^= 0x01
try:
    AESGCM(g["key"]).decrypt(g["nonce"], bytes(bad) + g["tag"], None)
    print("L4  flipped ciphertext byte: decrypted (unexpected)")
except InvalidTag:
    print("L4  flipped ciphertext byte: InvalidTag")

kdf = Argon2id(salt=b"somesalt", length=32, iterations=2, lanes=1, memory_cost=19456)
phc = kdf.derive_phc_encoded(b"correct horse battery staple")
print("L5  Argon2id (salt 'somesalt', t=2, m=19456, p=1, 32 B):", phc)
print("L5  passwords.verify_password(...) on it:", passwords.verify_password("correct horse battery staple", phc))

print("L6  To Base64 of SECRET:", compare.encode(compare.SECRET)["base64"])
print("L6  SHA2 (SHA-256) of SECRET:", compare.hash_(compare.SECRET))

print("L11 HS256 demo token (CyberChef JWT Verify):", " . ".join(tool_check.demo_hs256().split(".")))
print("L11 claims:", tool_check.DEMO_CLAIMS)

with tempfile.TemporaryDirectory() as d:  # lab 10 with SSLKEYLOGFILE set: what Wireshark will load
    keylog = Path(d) / "keylog.txt"
    env = dict(os.environ, SSLKEYLOGFILE=str(keylog))
    run = subprocess.run([sys.executable, "tls_localhost.py"], cwd=LABS / "L200/10-tls-localhost", env=env,
                         capture_output=True, encoding="utf-8", errors="replace", timeout=60, check=True)
    print("L10 lab output line 2:", run.stdout.splitlines()[1])
    labels = [ln.split()[0] for ln in keylog.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    print("L10 keylog labels:", {lab: labels.count(lab) for lab in sorted(set(labels))})

print("base64 check: 32-byte key ->", len(base64.b64encode(bytes(32))), "chars std,",
      len(base64.urlsafe_b64encode(bytes(32)).rstrip(b"=")), "chars base64url unpadded")
