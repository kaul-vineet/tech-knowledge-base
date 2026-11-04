"""Equivalent (pending CI): liboqs-python 0.16.0.1 (MIT) must interoperate with cryptography's FIPS 203 ML-KEM-768.
liboqs encapsulates to a cryptography public key, cryptography decapsulates - and the reverse. Sizes are compared too.
liboqs is for prototyping (its README); production code in this KB uses pyca/cryptography (OpenSSL 3.5+)."""
from cryptography.hazmat.primitives.asymmetric import mlkem


def crosscheck():
    import oqs  # pip install liboqs-python==0.16.0.1 (builds liboqs 0.16.0 on first import: needs git, CMake, a C compiler)
    ours = mlkem.MLKEM768PrivateKey.generate()
    with oqs.KeyEncapsulation("ML-KEM-768") as theirs:
        ct, ss = theirs.encap_secret(ours.public_key().public_bytes_raw())
        a = ours.decapsulate(ct) == ss
        their_pk = theirs.generate_keypair()
        ss2, ct2 = mlkem.MLKEM768PublicKey.from_public_bytes(their_pk).encapsulate()
        b = theirs.decap_secret(ct2) == ss2
        d = theirs.details
    return {"liboqs->cryptography": a, "cryptography->liboqs": b,
            "sizes": (d["length_public_key"], d["length_ciphertext"], d["length_shared_secret"])}


if __name__ == "__main__":
    try:
        print(crosscheck())
    except ImportError:
        print("liboqs-python not installed: skipped (CI ubuntu job installs liboqs-python==0.16.0.1)")
