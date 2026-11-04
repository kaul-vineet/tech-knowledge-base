## Why it matters
A config file holds `db_password: ZGJfcGFzc3dvcmQ9U3VwM3JTM2NyZXQ=`, labelled "encrypted". One `base64 -d` reveals it. Mixing up these three tools leaks secrets, makes passwords reversible, or hashes away data you need back.

## Mental model
Encoding is a **translator**, hashing a **shredder that keeps a fingerprint**, encryption a **locked safe**.

```
              reversible?        needs a key?
 ENCODING     yes, by anyone     no
 HASHING      no (one-way)       no
 ENCRYPTION   yes, key holders   yes
```

## How it works
1. **Encoding changes alphabet, not secrecy.** Base64 maps 3 bytes to 4 characters, hex 1 byte to 2; RFC 4648 says base encoding gives no confidentiality. `QWxhZGRpbjpvcGVuIHNlc2FtZQ==` decodes to `Aladdin:open sesame` with no key. It also costs space: 30 bytes become 40 base64 or 60 hex characters → see lab step 2.
2. **Encryption needs the key.** AES-GCM returns the exact bytes only to key holders; a wrong key raises `InvalidTag` → see lab step 3.
3. **Hashing is deterministic; encryption is randomised.** The same input always gives the same SHA-256 digest, so you compare digests, never "decrypt" them. A fresh nonce makes each encryption of the same input different → see lab step 4.

Pick by the question: need it back? Encrypt. Only compare? Hash (slow and salted for passwords). Binary into text? Encode.

## Common mistakes
- "Obfuscating" secrets in config or source with base64.
- Logging a base64 token and assuming the log is safe.
- Hashing a value you later need to show; encrypt it instead.
