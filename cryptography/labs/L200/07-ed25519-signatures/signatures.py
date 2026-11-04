"""Ed25519 detached signatures for a release file, key serialization, RFC 8032 test vector."""
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

# RFC 8032 section 7.1 TEST 1 (empty message)
RFC8032_T1 = {
    "secret": bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"),
    "public": bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"),
    "sig": bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
                         "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
}


def save_keys(key: Ed25519PrivateKey, folder: Path) -> None:
    # serialization: private = PKCS8 PEM (keep secret), public = SubjectPublicKeyInfo PEM (publish)
    (folder / "release.key").write_bytes(key.private_bytes(
        ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption()))
    (folder / "release.pub").write_bytes(key.public_key().public_bytes(
        ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo))


def load_public(path: Path) -> Ed25519PublicKey:
    return ser.load_pem_public_key(path.read_bytes())


def sign_file(key: Ed25519PrivateKey, path: Path) -> Path:
    sig_path = path.with_name(path.name + ".sig")
    sig_path.write_bytes(key.sign(path.read_bytes()))  # detached signature: 64 bytes, stored beside the file
    return sig_path


def verify_file(pub: Ed25519PublicKey, path: Path, sig_path: Path) -> bool:
    try:
        pub.verify(sig_path.read_bytes(), path.read_bytes())  # verify needs only the PUBLIC key
        return True
    except InvalidSignature:  # any changed byte in file or signature, or the wrong key
        return False


if __name__ == "__main__":
    v = Ed25519PrivateKey.from_private_bytes(RFC8032_T1["secret"])
    print("RFC 8032 TEST 1 public key:", v.public_key().public_bytes_raw() == RFC8032_T1["public"])
    print("RFC 8032 TEST 1 signature: ", v.sign(b"") == RFC8032_T1["sig"])  # Ed25519 is deterministic

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        signer = Ed25519PrivateKey.generate()  # signer keeps this; never ship it with the release
        save_keys(signer, d)
        print("sizes: raw private 32 B, raw public 32 B, PEM private",
              len((d / "release.key").read_bytes()), "B, PEM public", len((d / "release.pub").read_bytes()), "B")

        release = d / "app-1.0.tar.gz"
        release.write_bytes(b"pretend this is a release tarball\n" * 100)
        sig = sign_file(signer, release)
        pub = load_public(d / "release.pub")  # the verifier only ever loads the public key
        print("signature file:", sig.name, len(sig.read_bytes()), "bytes")
        print("verify original:       ", verify_file(pub, release, sig))
        print("verify with other key: ", verify_file(Ed25519PrivateKey.generate().public_key(), release, sig))
        release.write_bytes(release.read_bytes().replace(b"tarball", b"tarbaII", 1))
        print("verify after 1 change: ", verify_file(pub, release, sig))
