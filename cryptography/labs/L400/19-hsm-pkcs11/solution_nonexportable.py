"""Build-task solution: the TOKEN enforces non-exportable private keys; the application cannot opt out.
Private keys are always created CKA_SENSITIVE=True, CKA_EXTRACTABLE=False (so CKA_ALWAYS_SENSITIVE and
CKA_NEVER_EXTRACTABLE are True). A template that asks for anything else fails with CKR_TEMPLATE_INCONSISTENT."""
import soft_token as st
from soft_token import (CKA_ALWAYS_SENSITIVE, CKA_EXTRACTABLE, CKA_NEVER_EXTRACTABLE, CKA_SENSITIVE, CKA_VALUE,  # noqa: F401
                        CKM_ECDSA_SHA256, CKM_EDDSA, PKCS11Error)

ENFORCED = {CKA_SENSITIVE: True, CKA_EXTRACTABLE: False}


class HardenedSession(st.Session):
    def generate_key_pair(self, mechanism, label, private_template=None):
        asked = private_template or {}
        if any(k in asked and asked[k] != v for k, v in ENFORCED.items()):
            raise PKCS11Error("CKR_TEMPLATE_INCONSISTENT")  # token policy beats the application's template
        return super().generate_key_pair(mechanism, label, {**asked, **ENFORCED})


class SoftToken(st.SoftToken):
    def open_session(self):
        return HardenedSession(self)


if __name__ == "__main__":
    token = SoftToken("kb-l19", so_pin="so-demo-1234", user_pin="user-demo-5678")
    s = token.open_session()
    s.login("USER", "user-demo-5678")
    pub, priv = s.generate_key_pair(CKM_EDDSA, "release-signing")
    print("attributes:", {a: s.get_attribute_value(priv, a) for a in (CKA_SENSITIVE, CKA_EXTRACTABLE, CKA_ALWAYS_SENSITIVE, CKA_NEVER_EXTRACTABLE)})
    for what, call in (("read CKA_VALUE", lambda: s.get_attribute_value(priv, CKA_VALUE)),
                       ("wrap (export) the key", lambda: s.wrap_key(pub, priv)),
                       ("flip CKA_EXTRACTABLE back on", lambda: s.set_attribute_value(priv, CKA_EXTRACTABLE, True)),
                       ("template asking extractable", lambda: s.generate_key_pair(CKM_EDDSA, "x", {CKA_EXTRACTABLE: True}))):
        try:
            call()
            print(f"{what}: allowed (bad!)")
        except PKCS11Error as e:
            print(f"{what}: {e}")
    print("signing via handle still works:", len(s.sign(priv, CKM_EDDSA, b"release 1.4.0")), "byte signature")
