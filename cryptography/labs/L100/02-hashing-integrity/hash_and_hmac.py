"""SHA-256 of strings and files, tamper detection, and HMAC with constant-time compare."""
import hashlib
import hmac
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# Known-answer vectors: NIST FIPS 180 example ("abc") and RFC 4231 test case 2 (HMAC-SHA-256)
NIST_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
RFC4231_TC2 = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
# The OS's own SHA-256 tool: Linux coreutils, macOS shasum, Windows certutil (first one found wins)
OS_TOOLS = (["sha256sum"], ["shasum", "-a", "256"], ["certutil", "-hashfile", "{path}", "SHA256"])


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()  # fixed output: any input -> 32 bytes (64 hex)


def sha256_file(path, chunk_size: int = 64 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):  # streaming: constant memory
            h.update(chunk)
    return h.hexdigest()


def os_sha256(path):
    """Return (tool, digest) from the OS's own hashing tool, or (None, None) if none is installed."""
    for tool in OS_TOOLS:
        if shutil.which(tool[0]):
            cmd = [str(path) if a == "{path}" else a for a in tool]
            if "{path}" not in tool:
                cmd.append(str(path))
            # explicit encoding + timeout: Windows would otherwise decode with the ANSI code page; never hang
            out = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace",
                                 timeout=30, check=True).stdout
            m = re.search(r"\b[0-9a-fA-F]{64}\b", out)  # each tool prints a different layout/case
            return tool[0], (m.group(0).lower() if m else None)
    return None, None


def hmac_sha256(key: bytes, msg: bytes) -> str:
    return hmac.new(key, msg, hashlib.sha256).hexdigest()  # HMAC: secret key mixed in -> only key holders can tag


def verify_hmac(key: bytes, msg: bytes, tag_hex: str) -> bool:
    # constant-time compare: never use == for secrets/tags; compare_digest avoids content-based early exit.
    return hmac.compare_digest(hmac_sha256(key, msg), tag_hex)


if __name__ == "__main__":
    print("sha256('abc')       ", sha256_text("abc"), sha256_text("abc") == NIST_ABC)
    print("sha256('')          ", sha256_text(""), sha256_text("") == EMPTY)

    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "release.bin"
        path.write_bytes(b"A" * 1_000_000)
        published = sha256_file(path)
        print("file (python)       ", published)
        tool, digest = os_sha256(path)
        print("file (OS tool)      ", digest, "via", tool)
        with open(path, "rb") as f:  # Python 3.11+ helper, same result
            print("stdlib file_digest  ", hashlib.file_digest(f, "sha256").hexdigest())
        with open(path, "r+b") as f:  # attacker flips one byte
            f.seek(500_000)
            f.write(b"B")  # avalanche: one changed byte -> completely different digest
        print("after 1-byte tamper ", sha256_file(path), "MATCH" if sha256_file(path) == published else "MISMATCH -> tampered")

    tag = hmac_sha256(b"Jefe", b"what do ya want for nothing?")
    print("HMAC RFC4231 TC2    ", tag, tag == RFC4231_TC2)
    key = os.urandom(32)
    t = hmac_sha256(key, b"amount=100")
    print("verify good msg     ", verify_hmac(key, b"amount=100", t))
    print("verify edited msg   ", verify_hmac(key, b"amount=900", t))
    print("verify wrong key    ", verify_hmac(os.urandom(32), b"amount=100", t))
