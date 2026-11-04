"""Sign a release: a manifest of SHA-256 digests, signed once with Ed25519, checked by the install step.
The install step below verifies the signature but trusts the folder (the fault); the build task makes it strict."""
import base64
import hashlib
import json
import random
import shutil
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SEED = 14
META = {"MANIFEST.json", "MANIFEST.json.sig"}


class Rejected(Exception):
    pass


def key_id(pub) -> str:
    return hashlib.sha256(pub.public_bytes_raw()).hexdigest()[:16]  # same key ID as lesson 7's keyring


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):  # stream: artifacts can be large
            h.update(chunk)
    return h.hexdigest()


def build_artifacts(dist: Path, seed=SEED) -> None:
    rng = random.Random(seed)  # seeded "build": same bytes every run
    for rel in ("app/__init__.py", "app/core.py", "app/data.json", "README.txt"):
        (dist / rel).parent.mkdir(parents=True, exist_ok=True)
        (dist / rel).write_bytes(f"# {rel} build {rng.randrange(10**6)}\n".encode() * 20)


def files_in(dist: Path) -> list:
    return sorted(p.relative_to(dist).as_posix() for p in dist.rglob("*") if p.is_file())  # '/' on Windows too


def sign_release(dist: Path, key: Ed25519PrivateKey, version: str) -> None:
    files = {rel: {"sha256": digest(dist / rel), "size": (dist / rel).stat().st_size}
             for rel in files_in(dist) if rel not in META}
    raw = json.dumps({"name": "demo-app", "version": version, "files": files}, sort_keys=True, indent=1).encode()
    (dist / "MANIFEST.json").write_bytes(raw)  # one signature covers every digest listed here
    sig = {"kid": key_id(key.public_key()), "sig": base64.b64encode(key.sign(raw)).decode()}
    (dist / "MANIFEST.json.sig").write_text(json.dumps(sig), encoding="utf-8")


def verified_manifest(dist: Path, trusted: dict) -> dict:
    raw = (dist / "MANIFEST.json").read_bytes()
    sig = json.loads((dist / "MANIFEST.json.sig").read_text(encoding="utf-8"))
    if sig["kid"] not in trusted:  # signer keyring: rotation = add the new kid, later remove the old one
        raise Rejected(f"unknown signer {sig['kid']}")
    try:
        trusted[sig["kid"]].verify(base64.b64decode(sig["sig"]), raw)  # verify the exact bytes, then parse
    except InvalidSignature:
        raise Rejected("manifest signature invalid") from None
    return json.loads(raw)


def install(dist: Path, target: Path, trusted: dict) -> list:
    """BUG on purpose: checks the signature and that listed files exist, then copies the whole folder."""
    manifest = verified_manifest(dist, trusted)
    for rel in manifest["files"]:
        if not (dist / rel).is_file():
            raise Rejected(f"missing {rel}")
    copied = [rel for rel in files_in(dist) if rel not in META]
    for rel in copied:
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dist / rel, target / rel)
    return copied


def tamper(dist: Path, seed=SEED) -> str:
    rel = random.Random(seed).choice([r for r in files_in(dist) if r not in META])  # seeded: same victim each run
    (dist / rel).write_bytes(b"import os  # attacker payload\n")  # swap content, keep name and old manifest + sig
    (dist / "app" / "zz_extra.pth").write_bytes(b"import app.core  # auto-runs at start-up\n")  # unlisted file
    return rel


def attempt(label, dist, trusted):
    with tempfile.TemporaryDirectory() as tmp:
        try:
            print(f"{label:<28} installed {len(install(dist, Path(tmp), trusted))} files")
        except Rejected as e:
            print(f"{label:<28} REJECTED: {e}")


if __name__ == "__main__":
    signer = Ed25519PrivateKey.generate()  # CI release key; the private key never ships
    trusted = {key_id(signer.public_key()): signer.public_key()}  # what the installer pins
    with tempfile.TemporaryDirectory() as tmp:
        dist = Path(tmp)
        build_artifacts(dist)
        sign_release(dist, signer, "1.0.0")
        print("manifest lists", len(json.loads((dist / "MANIFEST.json").read_bytes())["files"]), "files; signer", key_id(signer.public_key()))
        attempt("clean release", dist, trusted)
        stranger = Ed25519PrivateKey.generate().public_key()
        attempt("installer pins another key", dist, {key_id(stranger): stranger})
        print("fault: attacker swapped", tamper(dist), "and added app/zz_extra.pth; manifest + signature unchanged")
        attempt("tampered release", dist, trusted)
