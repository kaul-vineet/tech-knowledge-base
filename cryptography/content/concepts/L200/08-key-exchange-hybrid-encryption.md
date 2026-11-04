## Why it matters
A colleague needs the new database password, but you share no secret, and L100's AEAD needs one. Hybrid encryption lets you encrypt to their public key alone. age, HPKE (RFC 9180) and TLS 1.3 work this way.

## Mental model
**A padlock anyone can snap shut, but only its owner can open.** Each message gets a throwaway key.

```
sender:   eph (new) ─X25519(eph, B)─► shared ─HKDF─► key ─AEAD─► eph_pub ‖ ct ‖ tag
receiver: X25519(b, eph_pub) ───────► same shared ─HKDF─► key ─open─► plaintext
```

## How it works
1. **Key agreement.** X25519 combines your private key with their public key, and both sides get the same 32-byte secret. Public keys alone cannot reveal it → see lab step 1.
2. **Ephemeral key.** The sender makes a fresh key pair per message and puts its 32-byte public half in front. That is why sealing twice gives different blobs → see lab steps 2 and 4.
3. **KDF, never the raw secret.** HKDF-SHA256 derives the AEAD key. Its salt binds both public keys and its `info` label the protocol version, as in age (`age-encryption.org/v1/X25519`) → see lab step 2.
4. **AEAD.** ChaCha20-Poly1305 encrypts with a zero nonce, which is safe only because each key is used once. A wrong recipient, a changed AAD or a swapped ephemeral key all raise `InvalidTag` → see lab step 3.
5. **Degenerate keys.** RFC 7748 allows aborting on an all-zero shared secret. pyca already refuses one with `ValueError` → see lab step 5.

Worked example (RFC 7748 §6.1): Alice's secret `77076d0a…2c2a` and Bob's public key `de9edb7d…2b4f` give K = `4a5d9d5b…1742`, as Bob also computes. The lab's HKDF turns it into a key starting `d35fee1f`. The overhead is always 48 bytes: a 32-byte ephemeral key plus a 16-byte tag.

## Trade-offs
| Use when | Avoid when |
|---|---|
| You only have the recipient's public key (files, backups) | Parties talk interactively: use TLS |
| You can use age or an RFC 9180 HPKE library | You would invent a production wire format |
| One payload goes to several recipients (wrap a file key each) | The receiver must know the sender: base mode does not authenticate the sender |

## Common mistakes
- Using the X25519 output directly as a key, with no KDF.
- Reusing one ephemeral key while keeping the zero nonce.
- Assuming the receiver knows the sender. Sign it too.
