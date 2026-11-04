## Why it matters
You store `card=4111-1111` encrypted in a database row with `user_id=42` beside it. An attacker with write access can't read the card, but could flip ciphertext bits or copy the row to `user_id=43`. Plain encryption doesn't notice. AEAD does: decryption returns the exact plaintext or fails.

## Mental model
AEAD is a **tamper-evident sealed envelope**: the letter is secret, the address label (AAD) is readable but glued to the seal.

```
 key + nonce (12 B, never reused) + plaintext + AAD
      ──► encrypt ──► ciphertext ‖ tag (16 B)
 decrypt(...) ──► plaintext   or   InvalidTag
```

## How it works
1. **One call, two guarantees.** `encrypt()` returns ciphertext with a 16-byte tag appended; you store the 12-byte nonce in front, so a 14-byte message becomes a 42-byte blob → see lab step 2.
2. **All-or-nothing decrypt.** A changed ciphertext bit, key, nonce or AAD raises `InvalidTag`; changing `user_id=42` to `43` in the AAD is enough → see lab steps 3-4.
3. **Nonce = number used once.** Reuse a nonce under the same key and the keystream repeats, so XOR of ciphertexts equals XOR of plaintexts. For `attack at dawn!!` / `retreat at dusk!` both XORs are `13110013…1d4a00` (`research/concept_examples.py`), so knowing one message reveals the other → see lab step 5.

## Common mistakes
- A hard-coded or reset-to-zero nonce counter under the same key.
- Forgetting to store the nonce, or decrypting with different AAD.
- Truncating the tag; RFC 8439 says it MUST NOT be done.
