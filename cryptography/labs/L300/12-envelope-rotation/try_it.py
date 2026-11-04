"""Try it: two experiments on envelope encryption (run: python try_it.py)."""
from cryptography.exceptions import InvalidTag

import envelope as env

ring = env.Keyring()
rec = env.seal(ring, b"card=4111-1111", "order-1")
ring.rotate()

# 1) Edit the header so a v1 record claims to be wrapped by v2. Does the v2 KEK open it?
try:
    env.open_(ring, {**rec, "kid": "orders-kek:v2"})
    print("1) relabelled header: decrypted (bad!)")
except InvalidTag:
    print("1) relabelled header: InvalidTag - the kid is bound to the wrapped DEK as AAD")

# 2) How many bytes does a rewrap re-encrypt, compared with re-encrypting the data itself?
records, size = 1000, 4096
wrapped = len(env.base64.b64decode(rec["wdek"]))
print(f"2) wrapped DEK = {wrapped} B (12 nonce + 32 key + 16 tag); rewrapping {records} x {size} B records "
      f"re-encrypts {records * 32:,} key bytes instead of {records * size:,} data bytes")
