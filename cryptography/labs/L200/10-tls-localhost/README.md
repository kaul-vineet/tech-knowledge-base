# 10 – TLS on localhost

Read first: `content/concepts/L200/10-tls-on-localhost.md`. Full lesson (steps, walkthrough, sources): `content/L200.json` (lesson 10).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python tls_localhost.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2)
```
Python ssl uses OpenSSL 3.3.7 7 Apr 2026
trusted CA       TLSv1.3 TLS_AES_256_GCM_SHA384 (256-bit) -> b'hello over TLS\n'
wrong hostname   REFUSED verify_code=62: Hostname mismatch, certificate is not valid for 'example.com'.
untrusted CA     REFUSED verify_code=20: unable to get local issuer certificate
```
Tests:
```
Ran 7 tests in 0.120s
OK (skipped=1)
```

**Equivalent: openssl s_client**

macOS (zsh):
```zsh
brew install openssl@3
$(brew --prefix openssl@3)/bin/openssl s_client -connect 127.0.0.1:8443 -servername localhost -CAfile pki/ca.pem -verify_return_error -brief </dev/null
```
Windows (PowerShell):
```powershell
winget install -e --id ShiningLight.OpenSSL.Light
$null | openssl s_client -connect 127.0.0.1:8443 -servername localhost -CAfile pki\ca.pem -verify_return_error -brief
```

## Build task
Mutual TLS: add make_pki_with_client(), mtls_server_context() (CERT_REQUIRED + load_verify_locations), start_mtls_server(ctx, seen) recording the client CN, and connect_mtls(port, pki, with_cert).

Hints: Client side: ctx.load_cert_chain(client.pem, client-key.pem). · Server side: tls.getpeercert()['subject'] holds the client CN after the handshake.

Reference solution: `solution_mtls.py` (passes: `Ran 2 tests in 0.348s` → OK). Test **your** `tls_localhost.py`:

macOS (zsh): `BUILD_IMPL=tls_localhost python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="tls_localhost"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

Before you add the feature this fails on purpose (observed: `FAILED (errors=2)`).

## Try it (predict first)
1. Cap the client at TLS 1.2 (maximum_version) and connect. *Predict:* TLSv1.2 with an ECDHE + AES-GCM suite.
2. Connect with server_hostname='127.0.0.1' instead of 'localhost'. *Predict:* Works: the SAN contains IP 127.0.0.1.

```bash
python try_it.py
```
Observed locally:
```
1) client max TLS 1.2 -> TLSv1.2 ECDHE-ECDSA-AES256-GCM-SHA384
2) server_hostname='127.0.0.1' -> TLSv1.3 b'hello over TLS\n'
```

## If it fails
| Symptom | Action |
|---|---|
| CERTIFICATE_VERIFY_FAILED in requests/httpx against your local server | Pass the lab CA: verify='pki/ca.pem' (or REQUESTS_CA_BUNDLE); never verify=False. |
| Unsure which CA file Python trusts by default | python -c "import ssl; print(ssl.get_default_verify_paths())" - the lab passes cafile= explicitly instead. |

## Look inside with Wireshark (learningTools)
`ssl.create_default_context()` (used by the client in `connect()`) writes TLS secrets to the file named in `SSLKEYLOGFILE`
(Python 3.8+, per the Python `ssl` docs). Start a loopback capture with display filter `tls`, then run:
```zsh
SSLKEYLOGFILE=keylog.txt python tls_localhost.py
```
```powershell
$env:SSLKEYLOGFILE="$PWD\keylog.txt"; python tls_localhost.py; Remove-Item Env:SSLKEYLOGFILE
```
Observed locally (no Wireshark in the sandbox; label counts in `keylog.txt`):
```
CLIENT_HANDSHAKE_TRAFFIC_SECRET 1 | SERVER_HANDSHAKE_TRAFFIC_SECRET 3 | CLIENT_TRAFFIC_SECRET_0 1 | SERVER_TRAFFIC_SECRET_0 1 | EXPORTER_SECRET 1
```
Three handshakes started; only the trusted-CA one reached application traffic keys. Load `keylog.txt` in Wireshark
(Preferences → Protocols → TLS) to see the TLS 1.3 handshake, the cipher suite and the decrypted `hello over TLS`
(pending a manual run). Delete `keylog.txt` afterwards: it decrypts the capture.
