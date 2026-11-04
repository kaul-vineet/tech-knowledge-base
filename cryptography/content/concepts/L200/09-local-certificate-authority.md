## Why it matters
Your services talk HTTPS on a laptop or a private network. Public CAs will not certify `localhost`. Self-signed leaf certificates trigger warnings, and teams "fix" those by turning verification off. A local CA keeps verification on: you trust one root, and every service gets a properly issued certificate.

## Mental model
A certificate is a **notarised ID card**: "this public key belongs to `localhost`, valid from A to B, for server use", signed by a notary. Verifiers trust only the notaries in their store.

```
 root CA (self-signed, CA:TRUE, keyCertSign) ──signs──► leaf: SAN localhost, 127.0.0.1
 verifier(store=[root], hostname, time) ──► chain [leaf, root] | VerificationError
```

## How it works
1. **Self-signed root.** Its issuer equals its subject. `BasicConstraints CA:TRUE, path_length=0` and `KeyUsage keyCertSign` let it sign leaf certificates only → see lab step 1.
2. **Name in the SAN.** Clients match the `subjectAltName` (DNS or IP), not the CN. The leaf also carries `CA:FALSE`, `digitalSignature`, the EKU `serverAuth` and 30 days of validity → see lab step 1.
3. **Path validation.** `PolicyBuilder().store().time().build_server_verifier(DNSName(...))` checks signatures, dates, extensions and the name → see lab step 2.
4. **Specific failures.** A wrong host, an expired certificate and an unknown root each give a different error → see lab step 3. In agent assist a local model explains these errors, but code decides the category → see lab step 5.
5. **Private keys stay private.** `server-key.pem` and the root key never leave the machine or enter a prompt → see lab step 4.

Worked example (one lab run): the `localhost` leaf verifies with a chain of length 2. Asking for `example.com` gives "leaf certificate has no matching subjectAltName". Checking 31 days later gives "cert is not valid at validation time".

## Trade-offs
| Use when | Avoid when |
|---|---|
| Dev, CI and internal mTLS where you control every trust store | The site is public: use ACME (e.g. Let's Encrypt) |
| You want scripted, short-lived certificates (step-ca, mkcert) | You cannot protect the root key: anyone holding it can impersonate any site to your machines |
| You test failures on purpose | One fixed peer: pinning may be simpler |

## Common mistakes
- Putting the hostname only in the CN. Verifiers check the SAN.
- Making a leaf `CA:TRUE`, or a root without `keyCertSign`. pyca rejects the root ("missing required extension").
- Giving leaf certificates multi-year validity, then forgetting them.
