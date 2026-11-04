# Lab 10 – Authentication with OpenID Connect (authorization code + PKCE)

> **`mock_idp.py` is a LEARNING-ONLY mock.** It has no login page, uses plain HTTP on 127.0.0.1 and HS256 tokens signed with the client secret. Never deploy it or copy it into a product. Use a real OpenID Provider such as Keycloak (below) and a maintained OIDC client library.

The Library Loans web app is the **Relying Party**: it sends the user to the provider with `state`, `nonce` and a PKCE `code_challenge` (S256), exchanges the returned code with the `code_verifier`, then accepts the ID token only after checking signature, `iss`, `aud`, `exp`, `iat` and `nonce`.

## Files
| File | Purpose |
|---|---|
| `rp_client.py` | Relying Party: discovery, `start_login()`, `finish_login()` (lesson code) |
| `id_token_rules.py` | Claim checks: iss, aud, exp, iat, nonce, sub |
| `jwt_hs256.py` | JWS compact HS256 sign/verify with an algorithm allow-list |
| `mock_idp.py` | LEARNING-ONLY OpenID Provider: discovery, /authorize, /token |
| `app.py` | Demo: one login, then a code replay |
| `keycloak_check.py` | Checks a real provider's discovery document (Keycloak, pending-ci) |
| `test_oidc.py` | PKCE vector (RFC 7636 App. B), JWT, claim rules, full flow and attacks |
| `test_build_task.py` | Build task check (max_age / auth_time) |
| `solution/id_token_rules.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L200/10-oidc-authentication
python app.py
python -m unittest -v
```
## Expected output (observed 2026-10-28, Python 3.12.15, Linux)

Codes, state, nonce and secrets are random per run; the demo prints only their checks.

```
$ python app.py
mock IdP (LEARNING ONLY) at http://127.0.0.1:<port>
1 authorize request -> ['client_id', 'code_challenge', 'code_challenge_method', 'nonce', 'redirect_uri', 'response_type', 'scope', 'state']
2 redirect to RP    -> code of 43 chars, state matches: True
3 ID token accepted -> sub=member-m1 aud=library-web nonce ok, valid 300 s
4 same code again   -> LoginFailed: token endpoint 400: invalid_grant: code unknown or already used
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_auth_time_required_with_max_age (test_build_task.MaxAgeTest.test_auth_time_required_with_max_age) ... ok
test_old_rules_still_apply (test_build_task.MaxAgeTest.test_old_rules_still_apply) ... ok
test_recent_login_passes_old_login_fails (test_build_task.MaxAgeTest.test_recent_login_passes_old_login_fails) ... ok
test_with_tokens_from_the_mock_idp (test_build_task.MaxAgeTest.test_with_tokens_from_the_mock_idp) ... ok
test_without_max_age_nothing_changes (test_build_task.MaxAgeTest.test_without_max_age_nothing_changes) ... ok
test_each_rule (test_oidc.ClaimRulesTest.test_each_rule) ... ok
test_good_token (test_oidc.ClaimRulesTest.test_good_token) ... ok
test_code_is_single_use (test_oidc.FlowTest.test_code_is_single_use) ... ok
test_discovery_document (test_oidc.FlowTest.test_discovery_document) ... ok
test_happy_path (test_oidc.FlowTest.test_happy_path) ... ok
test_missing_pkce_is_refused_by_the_idp (test_oidc.FlowTest.test_missing_pkce_is_refused_by_the_idp) ... ok
test_rp_rejects_expired_token (test_oidc.FlowTest.test_rp_rejects_expired_token) ... ok
test_rp_rejects_token_for_another_audience (test_oidc.FlowTest.test_rp_rejects_token_for_another_audience) ... ok
test_state_mismatch_stops_before_token_request (test_oidc.FlowTest.test_state_mismatch_stops_before_token_request) ... ok
test_stolen_code_without_verifier_fails (test_oidc.FlowTest.test_stolen_code_without_verifier_fails) ... ok
test_unregistered_redirect_uri_is_not_followed (test_oidc.FlowTest.test_unregistered_redirect_uri_is_not_followed) ... ok
test_alg_none_is_rejected (test_oidc.JwtTest.test_alg_none_is_rejected) ... ok
test_round_trip_and_tampering (test_oidc.JwtTest.test_round_trip_and_tampering) ... ok
test_rfc7636_appendix_b_vector (test_oidc.PkceTest.test_rfc7636_appendix_b_vector) ... ok

----------------------------------------------------------------------
Ran 19 tests in 5.109s

OK
```

## Build task
Support `max_age` in `id_token_rules.validate_claims(..., max_age=None)`: when `max_age` is given, `auth_time` must be present and the login must not be older than `max_age` (plus the 60 s leeway). Use it for sensitive actions such as changing a member's address.

- Solution: `solution/id_token_rules.py` (read it only after trying).
- Check: `python -m unittest -v test_build_task` tests the solution by default. To test YOUR `id_token_rules.py`:
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
```
$ python -m unittest test_build_task   # against the solution, observed 2026-10-28
OK
```

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first (the tasks and predictions are in the lesson's `tryIt` field), then run. `try_it.py` never edits the lab files.
```
$ python try_it.py
[1] stolen code, wrong verifier -> token endpoint 400: invalid_grant: PKCE verification failed
[1] codes left at the IdP after the failed attempt -> 0
[2] aud=quiz-app -> aud ['quiz-app'] does not contain 'library-web'
```

## Keycloak, the real equivalent (pending-ci)
Not run in the sandbox (no container engine). CI starts Keycloak 26.8.1 and runs `keycloak_check.py` against the `master` realm's discovery document.
```bash
# Mac mini (zsh) - Podman machine started (lesson 1)
podman run -d --name kc -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.8.1 start-dev
python keycloak_check.py

# Windows (PowerShell)
podman run -d --name kc -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin `
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.8.1 start-dev
python keycloak_check.py

podman rm -f kc   # both: stop and remove
```
`start-dev` is Keycloak's development mode (HTTP, admin/admin); production needs TLS, a real database and strong admin credentials. Keycloak signs ID tokens with RS256 and publishes its keys at the `jwks_uri`.

## Mac mini and Windows
Inside an activated venv the commands are identical on both machines (`python3`/`py -3.12` also work outside a venv). Use `\` in paths on Windows. Tests bind 127.0.0.1 on port 0 and create scratch folders inside the lab folder, never in a system temp path.

## Troubleshooting
| Symptom | Action |
|---|---|
| `LoginFailed: state does not match this login attempt` | The callback belongs to another login (or a forged link). Start a new login. |
| `invalid_grant: code unknown or already used` | Codes work once; start a new login. |
| `token expired` right after login | Clock skew between machines; sync time (NTP). The lab allows 60 s leeway. |
| `keycloak_check.py`: connection refused | Keycloak needs 20-60 s to start; retry, or check `podman logs kc`. |
