"""Equivalent with OpenBao's transit engine (encryption as a service): rotate, rewrap, min_decryption_version.
Needs a dev server (see README; pending CI here). Uses BAO_ADDR / BAO_TOKEN like the bao CLI.
Paths from https://openbao.org/docs/api/secret/transit/ (docs v2.7.x)."""
import base64
import json
import os
import sys
import urllib.error
import urllib.request


def key_version(ciphertext: str) -> int:
    """'vault:v2:...' -> 2. The prefix is OpenBao's key ID header, like the lab's 'orders-kek:v2'."""
    prefix, version, _ = ciphertext.split(":", 2)
    if prefix != "vault" or not version.startswith("v"):
        raise ValueError("not a transit ciphertext")
    return int(version[1:])


def api(path: str, body=None):
    req = urllib.request.Request(os.environ["BAO_ADDR"].rstrip("/") + "/v1/" + path, method="POST",
                                 data=json.dumps(body or {}).encode(),
                                 headers={"X-Vault-Token": os.environ["BAO_TOKEN"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read()
    return json.loads(raw).get("data") or {} if raw.strip() else {}  # some calls answer 204 No Content


def demo(key="orders-kl12"):
    api(f"transit/keys/{key}")  # create (default type aes256-gcm96)
    b64 = base64.b64encode(b"card=4111-1111").decode()
    c1 = api(f"transit/encrypt/{key}", {"plaintext": b64})["ciphertext"]
    api(f"transit/keys/{key}/rotate")
    c2 = api(f"transit/rewrap/{key}", {"ciphertext": c1})["ciphertext"]  # never returns plaintext
    print("encrypt ->", c1[:9], "| rotate + rewrap ->", c2[:9])
    api(f"transit/keys/{key}/config", {"min_decryption_version": 2})  # retire v1 for decryption
    print("decrypt rewrapped:", base64.b64decode(api(f"transit/decrypt/{key}", {"ciphertext": c2})["plaintext"]))
    try:
        api(f"transit/decrypt/{key}", {"ciphertext": c1})
        print("decrypt old v1: accepted (unexpected)")
    except urllib.error.HTTPError as e:
        print("decrypt old v1: refused, HTTP", e.code)
    return key_version(c1), key_version(c2)


if __name__ == "__main__":
    if not os.environ.get("BAO_ADDR") or not os.environ.get("BAO_TOKEN"):
        print("OpenBao not configured (set BAO_ADDR and BAO_TOKEN): skipped. Offline check:",
              "key_version('vault:v2:abc') =", key_version("vault:v2:abc"))
        sys.exit(0)
    print("versions:", demo())
