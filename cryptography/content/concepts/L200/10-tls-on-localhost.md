## Why it matters
Most crypto bugs in real applications are TLS configuration bugs, such as `verify=False` copied from a forum, `check_hostname = False`, or trusting every CA. Running TLS end to end on localhost with your own CA shows you what a correct handshake looks like, and exactly how it fails.

## Mental model
TLS is a **phone call where the callee shows ID first**. The client checks the ID, both sides agree a fresh key, and then every byte travels in AEAD records.

```
client(trust=ca.pem, want "localhost") ──ClientHello(SNI)──► server(cert + key)
        ◄── certificate chain + proof of private key ──
 chain + hostname ok ─► encrypted app data  |  fail ─► SSLCertVerificationError, no data
```

## How it works
1. **Server context.** `SSLContext(PROTOCOL_TLS_SERVER)` loads the lab-9 certificate and key and sets `minimum_version = TLSv1_2` → see lab step 1.
2. **Client context.** `create_default_context(cafile=ca.pem)` sets `CERT_REQUIRED` and `check_hostname=True`, and trusts only that CA. `server_hostname` sends SNI and is the name that gets checked → see lab step 1.
3. **Inspect.** `version()` and `cipher()` show what was negotiated. `TLS_AES_256_GCM_SHA384` is an AEAD suite, the L100 idea again → see lab step 1.
4. **Fail closed.** With a wrong name or an unknown CA the client aborts before any data arrives. `verify_code` and `verify_message` say why → see lab steps 2 and 3.
5. **CLI equivalent.** `openssl s_client` against `--serve` shows the same chain and errors. macOS `/usr/bin/openssl` is LibreSSL, so use Homebrew `openssl@3` for identical options → see lab step 4.

Worked example (one lab run, Python linked to OpenSSL 3.3.7): the trusted connection negotiates `TLSv1.3 TLS_AES_256_GCM_SHA384 (256-bit)`. Asking for `example.com` gives verify_code 62, "Hostname mismatch". A different CA gives verify_code 20, "unable to get local issuer certificate".

## Trade-offs
| Use when | Avoid when |
|---|---|
| Service-to-service traffic: TLS 1.2+ with verification is the baseline | You want to skip verification "for dev": trust a dev CA instead |
| You also need client identity: add mTLS (build task) | The client cannot load a CA file: fix distribution, do not skip checks |
| You can rely on library defaults | You would hand-pick cipher lists without a reason |

## Common mistakes
- Using `CERT_NONE` or `check_hostname=False`. The session is then encrypted but unauthenticated.
- Connecting by IP when the SAN lists only DNS names, or the reverse.
- Expecting LibreSSL `s_client` on a Mac to match OpenSSL 3 flags and wording.
