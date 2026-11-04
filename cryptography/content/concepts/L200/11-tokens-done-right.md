## Why it matters
A login service issues tokens that five APIs accept. If one API trusts the token's own `alg` header, an attacker can send `alg:none`, or HMAC-sign with your *public* key, and become admin. RFC 8725 (JWT Best Current Practices) exists because libraries shipped these bugs.

## Mental model
A signed token is a **visitor badge with a tamper seal**. Anyone can read it. The guard checks the seal with a key it chose, then the date and the door.

```
 header.payload.signature   (base64url, readable by anyone)
 verify: alg ∈ allow-list → key for THAT alg → signature → exp/nbf → aud → claims
```

## How it works
1. **Format.** The token is base64url(header).base64url(claims).base64url(signature), and the signature covers both parts. Signed is not encrypted: anyone can decode the claims → see lab step 1.
2. **Allow-list.** The verifier picks the algorithm, not the token. In the lab's `keys` map each allowed alg has exactly one key, so `none` and unexpected algs are rejected before any crypto runs → see lab step 2.
3. **Key confusion.** The naive verifier uses "the key" for whatever alg the header names. An HS256 token MACed with the public Ed25519 key bytes then passes. One key per alg stops this → see lab step 3.
4. **Claims after the signature.** `exp` is required here and gets a small clock-skew leeway. Then come `nbf` and an `aud` that must name this service → see lab step 4.
5. **Library equivalent.** PyJWT needs `algorithms=[...]` and `audience=...`. PyJWT and the lab code accept each other's tokens → see lab step 5.

Worked example (one lab run): an EdDSA token is 211 characters, 86 of them signature. The forged `alg:none` header is 35 characters starting `eyJhbG`. The naive verifier accepts `role=admin`; the safe one answers "algorithm 'none' not allowed".

## Trade-offs
| Use when | Avoid when |
|---|---|
| Short-lived (minutes) stateless authorization between services | You need instant revocation: use sessions or short tokens + refresh |
| One issuer, many verifiers: EdDSA/ES256 (only the issuer can mint) | Every verifier holding an HS256 secret could also mint tokens |
| A maintained library with allow-list + aud + exp | Using this lab code in production |

## Common mistakes
- Calling `decode()` without an algorithm list, or with signature checks off.
- Skipping `aud`, so a `billing-api` token works on `orders-api`.
- Putting secrets or personal data in claims.
