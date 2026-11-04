"""Password storage: Argon2id (PHC string) with OWASP minimums, scrypt as fallback."""
import base64
import os
import time

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# OWASP Password Storage Cheat Sheet minimums (checked 2026-10-28)
ARGON2ID = {"memory_cost": 19456, "iterations": 2, "lanes": 1}  # slow + memory-hard: m=19 MiB, t=2, p=1
SCRYPT = {"n": 2**17, "r": 8, "p": 1}                            # 128 MiB
SALT_BYTES = 16                                                  # unique salt per password; RFC 9106: 16 B


def hash_password(password: str) -> str:
    kdf = Argon2id(salt=os.urandom(SALT_BYTES), length=32, **ARGON2ID)
    return kdf.derive_phc_encoded(password.encode())  # self-describing PHC string: $argon2id$v=19$m=..,t=..,p=..$salt$hash


def verify_password(password: str, stored: str) -> bool:
    try:
        Argon2id.verify_phc_encoded(password.encode(), stored)  # params+salt read from the string
        return True
    except InvalidKey:
        return False


def scrypt_hash(password: str) -> str:
    salt = os.urandom(SALT_BYTES)
    dk = Scrypt(salt=salt, length=32, **SCRYPT).derive(password.encode())
    b64 = lambda b: base64.b64encode(b).decode()
    return f"scrypt${SCRYPT['n']}${SCRYPT['r']}${SCRYPT['p']}${b64(salt)}${b64(dk)}"


def scrypt_verify(password: str, stored: str) -> bool:
    _, n, r, p, salt, dk = stored.split("$")
    try:
        Scrypt(salt=base64.b64decode(salt), length=32, n=int(n), r=int(r), p=int(p)).verify(
            password.encode(), base64.b64decode(dk))  # constant-time comparison inside
        return True
    except InvalidKey:
        return False


def rfc9106_argon2id_vector() -> str:
    # RFC 9106 section 5.3 inputs (tiny parameters: test only, never production)
    kdf = Argon2id(salt=b"\x02" * 16, length=32, iterations=3, lanes=4, memory_cost=32,
                   ad=b"\x04" * 12, secret=b"\x03" * 8)
    return kdf.derive(b"\x01" * 32).hex()


def rfc7914_scrypt_vector() -> str:
    return Scrypt(salt=b"NaCl", length=64, n=1024, r=8, p=16).derive(b"password").hex()


if __name__ == "__main__":
    print("RFC 9106 Argon2id tag:", rfc9106_argon2id_vector())
    print("RFC 7914 scrypt  dk  :", rfc7914_scrypt_vector()[:32], "...")
    t = time.perf_counter()
    h1 = hash_password("correct horse battery staple")
    print(f"argon2id hash ({time.perf_counter() - t:.3f}s):", h1)
    h2 = hash_password("correct horse battery staple")
    print("same password, new salt -> different hash:", h1 != h2)
    print("verify right password:", verify_password("correct horse battery staple", h1))
    print("verify wrong password:", verify_password("Correct horse battery staple", h1))
    t = time.perf_counter()
    s = scrypt_hash("hunter2")
    print(f"scrypt fallback ({time.perf_counter() - t:.3f}s):", s)
    print("scrypt verify right/wrong:", scrypt_verify("hunter2", s), scrypt_verify("hunter3", s))
