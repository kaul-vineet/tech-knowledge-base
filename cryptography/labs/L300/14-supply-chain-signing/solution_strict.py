"""Build task solution: the install step checks EVERY file against the signed manifest before copying anything."""
import hmac
import shutil
from pathlib import Path

from release_sign import META, Rejected, digest, files_in, verified_manifest


def install(dist: Path, target: Path, trusted: dict) -> list:
    manifest = verified_manifest(dist, trusted)  # 1. signature by a pinned key over the exact manifest bytes
    listed, present = set(manifest["files"]), {rel for rel in files_in(dist) if rel not in META}
    if present - listed:  # 2. allow-list: a file the signer never listed is an attack, not a bonus
        raise Rejected(f"unknown file(s): {sorted(present - listed)}")
    if listed - present:
        raise Rejected(f"missing file(s): {sorted(listed - present)}")
    for rel in sorted(listed):  # 3. every digest and size, before anything is copied (no half-installs)
        want = manifest["files"][rel]
        if (dist / rel).stat().st_size != want["size"] or not hmac.compare_digest(digest(dist / rel), want["sha256"]):
            raise Rejected(f"digest mismatch: {rel}")
    for rel in sorted(listed):
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dist / rel, target / rel)
    return sorted(listed)


if __name__ == "__main__":
    import tempfile

    import release_sign as rs
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    signer = Ed25519PrivateKey.generate()
    trusted = {rs.key_id(signer.public_key()): signer.public_key()}
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as out:
        dist = Path(tmp)
        rs.build_artifacts(dist)
        rs.sign_release(dist, signer, "1.0.0")
        print("clean release:   ", len(install(dist, Path(out), trusted)), "files installed")
        rs.tamper(dist)
        try:
            install(dist, Path(out), trusted)
        except Rejected as e:
            print("tampered release: REJECTED:", e)
