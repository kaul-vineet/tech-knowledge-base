**Concept: Login with OpenID Connect (authorization code + PKCE)**

## Why it matters
Library Loans should not store passwords. It delegates login to an identity provider and receives an
ID token that says who logged in. The flow runs through browser redirects, where codes can leak and
links can be forged; each parameter closes one hole.

## Mental model
Think of a cloakroom ticket. You keep one half secret (the PKCE verifier) and the desk keeps a hash of it
(the challenge). The ticket (the code) is useless without your half, and it works only once.

```
RP: state, nonce, verifier ─► browser ─► IdP /authorize (code_challenge=S256(verifier))
RP ◄─ browser ◄─ 302 ?code&state
RP ── POST /token (code + verifier + client secret) ─► IdP checks S256(verifier) == challenge
RP ◄─ id_token ── checks: signature, iss, aud, exp, iat, nonce
```

## How it works
1. **Prepare.** `start_login` creates a random `state` (against CSRF), a `nonce` (to bind the token to this
   login) and a 43-character `code_verifier`. It sends only the verifier's S256 hash → see lab step 1
2. **Callback.** The RP checks `state` before anything else, then exchanges the code. The IdP redeems a
   code once, only for the same client, redirect URI and verifier → see lab step 2
3. **Validate the ID token.** Check the signature with an algorithm from the RP's allow-list (never
   `none`), then `iss` exact match, `aud` contains our client id, `exp`/`iat` with small leeway, and
   `nonce` → see lab step 3
4. **Real provider.** Keycloak publishes the same endpoints through discovery and signs with RS256 keys
   from `jwks_uri` → see lab step 4

**Worked example** (`research/L200_concept_examples.py`): RFC 7636's verifier
`dBjftJeZ…` (43 characters) hashes to `E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM`. With 60 s
leeway, `exp = now − 59 s` passes and `exp = now − 61 s` gives "token expired".

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Users log in through a browser or a native app | Service-to-service calls (use client credentials) |
| You want single sign-on and MFA without storing passwords | You would hand-roll it in production (use a certified library) |
| Several apps share one identity provider | You only need an API key for an internal script |

## Common mistakes
- Accepting the token's own `alg` header, including `none`.
- Skipping `aud`, so a token minted for another app logs users into yours.
- Using the implicit flow or the `plain` PKCE method in new code.
