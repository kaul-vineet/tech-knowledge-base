"""Build task solution: id_token_rules.py plus max_age / auth_time checking.

When the RP sends max_age, the ID token MUST carry auth_time, and the login must not be older than max_age.
"""
import hmac


def validate_claims(claims, *, issuer, client_id, nonce, now, leeway=60, max_age=None):
    problems = []
    if claims.get("iss") != issuer:
        problems.append(f"iss {claims.get('iss')!r} is not the expected issuer {issuer!r}")
    audiences = claims.get("aud") if isinstance(claims.get("aud"), list) else [claims.get("aud")]
    if client_id not in audiences:
        problems.append(f"aud {audiences} does not contain {client_id!r}")
    if not isinstance(claims.get("exp"), (int, float)) or now >= claims["exp"] + leeway:
        problems.append(f"token expired (exp {claims.get('exp')}, now {int(now)})")
    if not isinstance(claims.get("iat"), (int, float)) or claims["iat"] > now + leeway:
        problems.append(f"iat {claims.get('iat')} is missing or in the future")
    if not hmac.compare_digest(str(claims.get("nonce", "")), nonce):
        problems.append("nonce does not match the one sent in the authentication request")
    if not claims.get("sub"):
        problems.append("sub is missing")
    if max_age is not None:  # the build task: recent-login requirement
        auth_time = claims.get("auth_time")
        if not isinstance(auth_time, (int, float)):
            problems.append("auth_time is required when max_age is used")
        elif now - auth_time > max_age + leeway:
            problems.append(f"login is {int(now - auth_time)} s old, max_age is {max_age} s")
    return problems
