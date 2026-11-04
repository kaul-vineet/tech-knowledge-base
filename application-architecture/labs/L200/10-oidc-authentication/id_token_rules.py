"""ID token claim checks a Relying Party runs AFTER the signature check (OpenID Connect Core 1.0, ID Token)."""
import hmac


def validate_claims(claims, *, issuer, client_id, nonce, now, leeway=60):
    """Return a list of problems ([] = the token may be trusted for this login)."""
    problems = []
    if claims.get("iss") != issuer:  # exact string match, no normalising
        problems.append(f"iss {claims.get('iss')!r} is not the expected issuer {issuer!r}")
    audiences = claims.get("aud") if isinstance(claims.get("aud"), list) else [claims.get("aud")]
    if client_id not in audiences:  # a token minted for another app must not log a user into ours
        problems.append(f"aud {audiences} does not contain {client_id!r}")
    if not isinstance(claims.get("exp"), (int, float)) or now >= claims["exp"] + leeway:
        problems.append(f"token expired (exp {claims.get('exp')}, now {int(now)})")
    if not isinstance(claims.get("iat"), (int, float)) or claims["iat"] > now + leeway:
        problems.append(f"iat {claims.get('iat')} is missing or in the future")
    if not hmac.compare_digest(str(claims.get("nonce", "")), nonce):  # binds the token to THIS login attempt
        problems.append("nonce does not match the one sent in the authentication request")
    if not claims.get("sub"):
        problems.append("sub is missing")
    return problems
