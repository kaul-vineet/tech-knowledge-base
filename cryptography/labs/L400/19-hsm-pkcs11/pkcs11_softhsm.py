"""Equivalent (pending CI): the same design against a real PKCS#11 module - SoftHSM2 2.7.0 (BSD-2-Clause) through
python-pkcs11 0.10.1 (MIT). Generates a P-256 key INSIDE the token with SENSITIVE=True / EXTRACTABLE=False, signs via
the handle, verifies with pyca/cryptography, and shows that reading the private value fails.
Setup (CI ubuntu job; Mac: brew install softhsm):
  softhsm2-util --init-token --free --label kb-l19 --so-pin 5678 --pin 1234
  export PKCS11_MODULE=/usr/lib/softhsm/libsofthsm2.so  (Homebrew: $(brew --prefix softhsm)/lib/softhsm/libsofthsm2.so)"""
import os

from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.asymmetric import ec

TOKEN_LABEL, USER_PIN = os.environ.get("PKCS11_TOKEN", "kb-l19"), os.environ.get("PKCS11_PIN", "1234")  # CI demo PIN


def run():
    import pkcs11
    from pkcs11 import Attribute, KeyType, Mechanism
    from pkcs11.util.ec import encode_ec_public_key, encode_ecdsa_signature, encode_named_curve_parameters

    lib = pkcs11.lib(os.environ["PKCS11_MODULE"])
    token = lib.get_token(token_label=TOKEN_LABEL)
    with token.open(user_pin=USER_PIN, rw=True) as session:
        params = session.create_domain_parameters(KeyType.EC, {Attribute.EC_PARAMS: encode_named_curve_parameters("secp256r1")}, local=True)
        pub, priv = params.generate_keypair(store=False, label="release-signing",
                                            private_template={Attribute.SENSITIVE: True, Attribute.EXTRACTABLE: False})
        sig = priv.sign(b"release 1.4.0", mechanism=Mechanism.ECDSA_SHA256)  # signing via the handle
        public = ser.load_der_public_key(encode_ec_public_key(pub))
        public.verify(encode_ecdsa_signature(sig), b"release 1.4.0", ec.ECDSA(hashes.SHA256()))  # raises if wrong
        try:
            priv[Attribute.VALUE]
            leaked = True
        except pkcs11.exceptions.AttributeSensitive:
            leaked = False
        return {"verified_with_cryptography": True, "private_value_readable": leaked,
                "never_extractable": bool(priv[Attribute.NEVER_EXTRACTABLE]), "always_sensitive": bool(priv[Attribute.ALWAYS_SENSITIVE])}


if __name__ == "__main__":
    if "PKCS11_MODULE" not in os.environ:
        print("PKCS11_MODULE not set: skipped (CI ubuntu job installs softhsm2 and python-pkcs11==0.10.1)")
    else:
        print(run())
