"""A PKCS#11-shaped software token: slots, PIN login, sessions, object HANDLES and attributes.
Applications get a handle and ask the token to sign; with CKA_SENSITIVE / CKA_EXTRACTABLE set right they can never
read the private key. LEARNING CODE: a software token protects nothing from a process that can read its memory -
the real boundary is SoftHSM2 / an HSM behind PKCS#11 (pkcs11_softhsm.py, pending CI)."""
import json
import random

from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

SEED = 19  # seeds the injected fault (which attribute the compromised app asks for first)
CKA_LABEL, CKA_SIGN, CKA_VALUE, CKA_CLASS = "CKA_LABEL", "CKA_SIGN", "CKA_VALUE", "CKA_CLASS"
CKA_SENSITIVE, CKA_EXTRACTABLE = "CKA_SENSITIVE", "CKA_EXTRACTABLE"
CKA_ALWAYS_SENSITIVE, CKA_NEVER_EXTRACTABLE = "CKA_ALWAYS_SENSITIVE", "CKA_NEVER_EXTRACTABLE"
CKM_EDDSA, CKM_ECDSA_SHA256 = "CKM_EDDSA", "CKM_ECDSA_SHA256"
MAX_PIN_TRIES = 3


class PKCS11Error(Exception):
    """Carries a PKCS#11 return value name, e.g. CKR_ATTRIBUTE_SENSITIVE."""


class SoftToken:
    def __init__(self, label: str, so_pin: str, user_pin: str):
        self.label, self._pins, self._tries = label, {"SO": so_pin, "USER": user_pin}, 0
        self._objects, self._next = {}, 1
        self.audit = []  # JSON events: who did what with which handle

    def open_session(self):
        return Session(self)

    def _log(self, **event):
        self.audit.append(json.dumps(event, sort_keys=True))


class Session:
    def __init__(self, token: SoftToken):
        self.t, self.user = token, None

    def login(self, user_type: str, pin: str):
        if self.t._tries >= MAX_PIN_TRIES:
            raise PKCS11Error("CKR_PIN_LOCKED")
        if pin != self.t._pins[user_type]:
            self.t._tries += 1
            self.t._log(op="C_Login", user=user_type, ok=False)
            raise PKCS11Error("CKR_PIN_INCORRECT")
        self.t._tries, self.user = 0, user_type
        self.t._log(op="C_Login", user=user_type, ok=True)

    def _new(self, attrs, key) -> int:
        h, self.t._next = self.t._next, self.t._next + 1
        self.t._objects[h] = {"attrs": attrs, "key": key}
        return h

    def generate_key_pair(self, mechanism: str, label: str, private_template=None):
        if self.user != "USER":
            raise PKCS11Error("CKR_USER_NOT_LOGGED_IN")  # the SO administers the token but cannot use keys
        key = ed25519.Ed25519PrivateKey.generate() if mechanism == CKM_EDDSA else ec.generate_private_key(ec.SECP256R1())
        # BUG on purpose: when the template omits them, defaults are "sensitive: no, extractable: yes"
        attrs = {CKA_CLASS: "CKO_PRIVATE_KEY", CKA_LABEL: label, CKA_SIGN: True, CKA_SENSITIVE: False, CKA_EXTRACTABLE: True,
                 **(private_template or {})}
        attrs[CKA_ALWAYS_SENSITIVE], attrs[CKA_NEVER_EXTRACTABLE] = attrs[CKA_SENSITIVE], not attrs[CKA_EXTRACTABLE]
        priv = self._new(attrs, key)
        pub = self._new({CKA_CLASS: "CKO_PUBLIC_KEY", CKA_LABEL: label, CKA_SENSITIVE: False}, key.public_key())
        self.t._log(op="C_GenerateKeyPair", label=label, mechanism=mechanism, handle=priv)
        return pub, priv

    def find_objects(self, label: str, cls: str = "CKO_PRIVATE_KEY") -> list:
        return [h for h, o in self.t._objects.items() if o["attrs"].get(CKA_LABEL) == label and o["attrs"][CKA_CLASS] == cls]

    def get_attribute_value(self, handle: int, attr: str):
        o = self.t._objects[handle]
        if attr == CKA_VALUE:
            if o["attrs"][CKA_CLASS] == "CKO_PUBLIC_KEY":
                return o["key"].public_bytes(ser.Encoding.DER, ser.PublicFormat.SubjectPublicKeyInfo)
            if o["attrs"][CKA_SENSITIVE] or not o["attrs"][CKA_EXTRACTABLE]:
                self.t._log(op="C_GetAttributeValue", attr=attr, handle=handle, ok=False)
                raise PKCS11Error("CKR_ATTRIBUTE_SENSITIVE")  # the key never leaves the token in plaintext
            self.t._log(op="C_GetAttributeValue", attr=attr, handle=handle, ok=True)
            return o["key"].private_bytes(ser.Encoding.DER, ser.PrivateFormat.PKCS8, ser.NoEncryption())
        return o["attrs"][attr]

    def set_attribute_value(self, handle: int, attr: str, value: bool):
        attrs = self.t._objects[handle]["attrs"]
        if (attr == CKA_SENSITIVE and attrs[attr] and not value) or (attr == CKA_EXTRACTABLE and not attrs[attr] and value):
            raise PKCS11Error("CKR_ATTRIBUTE_READ_ONLY")  # one-way switches: sensitive stays on, extractable stays off
        attrs[attr] = value
        attrs[CKA_ALWAYS_SENSITIVE] &= attrs[CKA_SENSITIVE]
        attrs[CKA_NEVER_EXTRACTABLE] &= not attrs[CKA_EXTRACTABLE]

    def wrap_key(self, wrapping_handle: int, handle: int) -> bytes:
        if not self.t._objects[handle]["attrs"][CKA_EXTRACTABLE]:
            raise PKCS11Error("CKR_KEY_UNEXTRACTABLE")
        return b"wrapped:" + self.get_attribute_value(handle, CKA_VALUE)[:8]  # placeholder: real tokens wrap with a key

    def sign(self, handle: int, mechanism: str, data: bytes) -> bytes:
        if self.user != "USER":
            raise PKCS11Error("CKR_USER_NOT_LOGGED_IN")
        o = self.t._objects[handle]
        if not o["attrs"].get(CKA_SIGN):
            raise PKCS11Error("CKR_KEY_FUNCTION_NOT_PERMITTED")
        self.t._log(op="C_Sign", handle=handle, mechanism=mechanism, bytes=len(data))
        return o["key"].sign(data) if mechanism == CKM_EDDSA else o["key"].sign(data, ec.ECDSA(hashes.SHA256()))

    def logout(self):
        self.user = None


if __name__ == "__main__":
    rng = random.Random(SEED)
    token = SoftToken("kb-l19", so_pin="so-demo-1234", user_pin="user-demo-5678")  # demo PINs only
    s = token.open_session()
    try:
        s.login("USER", "0000")
    except PKCS11Error as e:
        print("1) wrong PIN:", e)
    s.login("USER", "user-demo-5678")
    pub, priv = s.generate_key_pair(CKM_EDDSA, "release-signing")  # app relies on the token's defaults
    sig = s.sign(priv, CKM_EDDSA, b"release 1.4.0")
    print("2) signed via handle", priv, "| sig bytes:", len(sig), "| public key DER bytes:", len(s.get_attribute_value(pub, CKA_VALUE)))
    print("--- fault: a compromised app asks the token for the private key")
    ask = rng.sample([CKA_VALUE, CKA_EXTRACTABLE, CKA_SENSITIVE], 3)
    print("attributes:", {a: (len(v) if isinstance(v, bytes) else v) for a in ask for v in [s.get_attribute_value(priv, a)]})
    stolen = ser.load_der_private_key(s.get_attribute_value(priv, CKA_VALUE), None)
    s.logout()
    print("after logout the stolen key still signs offline:", stolen.sign(b"release 6.6.6") is not None,
          "| audit events:", len(token.audit))
