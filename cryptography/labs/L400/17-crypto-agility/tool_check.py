"""Fixed DEMO values for the CyberChef check: decrypt a v2 envelope's AES-256-GCM ciphertext by hand.
The AAD is the canonical header JSON, so changing one header field (e.g. the algorithm id) must fail."""
from cryptography.exceptions import InvalidTag

import agile_envelope as ae
import registry as reg

key, nonce = bytes(range(32)), bytes([17] * 12)  # demo only - never paste a real key into a web tool
header = {"v": 2, "aead": "A256GCM", "kid": "dk-1", "n": ae.b64e(nonce), "ctx": "doc-1"}
aad = ae.canon(header)
out = reg.aead("A256GCM", key).encrypt(nonce, b"invoice 1: amount=100", aad)
print("Key (hex):         ", key.hex())
print("IV (hex):          ", nonce.hex())
print("Ciphertext (hex):  ", out[:-16].hex())
print("GCM tag (hex):     ", out[-16:].hex())
print("AAD (UTF8):        ", aad.decode())
print("expected output:   ", reg.aead("A256GCM", key).decrypt(nonce, out, aad).decode())
try:
    reg.aead("A256GCM", key).decrypt(nonce, out, aad.replace(b"A256GCM", b"C20P1305"))
except InvalidTag:
    print("AAD with aead=C20P1305 must fail: yes, InvalidTag")
