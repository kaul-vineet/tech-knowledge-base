"""Fixed DEMO values for the CyberChef check: unwrap a DEK by hand (AES Decrypt, GCM, with tag and AAD).
Demo keys only - never paste a real KEK into any tool."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEK = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")  # DEMO KEK
DEK = bytes.fromhex("a0" * 32)  # DEMO data key
NONCE = bytes.fromhex("0c" * 12)  # fixed only so the values are reproducible
KID = "orders-kek:v1"

out = AESGCM(KEK).encrypt(NONCE, DEK, KID.encode())
print("Key (hex):         ", KEK.hex())
print("IV (hex):          ", NONCE.hex())
print("Ciphertext (hex):  ", out[:-16].hex())
print("GCM tag (hex):     ", out[-16:].hex())
print("AAD (UTF8):        ", KID)
print("expected output:   ", DEK.hex())
print("AAD 'orders-kek:v2' must fail:", end=" ")
try:
    AESGCM(KEK).decrypt(NONCE, out, b"orders-kek:v2")
    print("no")
except Exception as e:  # InvalidTag
    print("yes,", type(e).__name__)
