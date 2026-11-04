"""Files and values to cross-check tokens.py with independent tools (CyberChef, step CLI).

python tool_check.py [folder]   (default folder: tool_check)
- prints a FIXED HS256 demo token + its demo key -> paste both into CyberChef "JWT Verify"
- writes eddsa.jwt, none.jwt and issuer-pub.pem -> verify with `step crypto jwt verify`
The demo key is public on purpose (learning only); never paste a real key into a web tool.
"""
import sys
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import tokens

DEMO_KEY = b"lab11-demo-key-not-a-secret"  # HS256 shared secret, published for the exercise only
DEMO_CLAIMS = {"sub": "alice", "aud": "orders-api", "exp": 4102444800, "role": "user"}  # exp = 2100-01-01


def demo_hs256() -> str:
    return tokens.sign(DEMO_CLAIMS, "HS256", DEMO_KEY)  # deterministic: same token on every machine


def write_eddsa_files(folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    issuer = Ed25519PrivateKey.generate()  # fresh key each run; only the PUBLIC key is written
    claims = {"sub": "alice", "aud": "orders-api", "exp": int(time.time()) + 3600, "role": "user"}
    good = tokens.sign(claims, "EdDSA", issuer)
    none_header = tokens.b64u(b'{"alg":"none","typ":"JWT"}')
    none_tok = none_header + "." + good.split(".")[1] + "."  # alg none: same claims, empty signature
    (folder / "eddsa.jwt").write_text(good, encoding="utf-8")
    (folder / "none.jwt").write_text(none_tok, encoding="utf-8")
    (folder / "issuer-pub.pem").write_bytes(issuer.public_key().public_bytes(
        ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo))
    return {"good": good, "none": none_tok, "pub": issuer.public_key()}


if __name__ == "__main__":
    tok = demo_hs256()
    print("HS256 demo token:", tok)
    print("HS256 demo key  :", DEMO_KEY.decode())
    print("lab verify      :", tokens.verify(tok, {"HS256": DEMO_KEY}, "orders-api"))
    out = write_eddsa_files(Path(sys.argv[1] if len(sys.argv) > 1 else "tool_check"))
    print("EdDSA lab verify:", tokens.verify(out["good"], {"EdDSA": out["pub"]}, "orders-api")["sub"],
          "| files: eddsa.jwt, none.jwt, issuer-pub.pem")
