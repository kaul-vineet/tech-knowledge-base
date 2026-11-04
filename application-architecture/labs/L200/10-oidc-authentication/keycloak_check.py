"""Check an OpenID Provider's discovery document - the mock here, Keycloak in CI (pending-ci).

    python keycloak_check.py                     # KEYCLOAK_URL (default http://127.0.0.1:8080), realm master
Start Keycloak first (Podman or Docker):
    podman run -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
        quay.io/keycloak/keycloak:26.8.1 start-dev
"""
import json
import os
import sys
import urllib.request


def check_discovery(doc, issuer, signing_alg="RS256"):
    problems = []
    if doc.get("issuer") != issuer:
        problems.append(f"issuer {doc.get('issuer')!r} != {issuer!r}")
    for key in ("authorization_endpoint", "token_endpoint") + (("jwks_uri",) if signing_alg.startswith(("RS", "ES", "PS")) else ()):
        if not doc.get(key):
            problems.append(f"{key} missing")
    if "code" not in doc.get("response_types_supported", []):
        problems.append("response type 'code' not supported")
    if "S256" not in doc.get("code_challenge_methods_supported", []):  # RFC 9700: advertise PKCE support
        problems.append("PKCE S256 not advertised in code_challenge_methods_supported")
    if signing_alg not in doc.get("id_token_signing_alg_values_supported", []):
        problems.append(f"{signing_alg} not in id_token_signing_alg_values_supported")
    return problems


if __name__ == "__main__":
    base = os.environ.get("KEYCLOAK_URL", "http://127.0.0.1:8080").rstrip("/")
    issuer = f"{base}/realms/{os.environ.get('KEYCLOAK_REALM', 'master')}"
    with urllib.request.urlopen(f"{issuer}/.well-known/openid-configuration", timeout=10) as resp:
        doc = json.loads(resp.read())
    problems = check_discovery(doc, issuer)
    for problem in problems:
        print("PROBLEM", problem)
    print(f"{issuer}: {'OK' if not problems else 'FAILED'} (code flow, PKCE S256, RS256 ID tokens)")
    sys.exit(1 if problems else 0)
