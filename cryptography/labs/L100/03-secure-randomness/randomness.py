"""secrets vs random: generate tokens/keys/nonces, then break a predictable token."""
import random
import secrets
import time


def secure_material() -> dict:
    return {
        "api_token_urlsafe": secrets.token_urlsafe(32),  # CSPRNG: 32 OS-random bytes = 256 bits -> ~43 chars
        "session_id_hex": secrets.token_hex(16),
        "aes256_key": secrets.token_bytes(32),
        "gcm_nonce": secrets.token_bytes(12),  # 96-bit nonce for AES-GCM / ChaCha20-Poly1305
        "pin_6_digits": f"{secrets.randbelow(10**6):06d}",
    }


def insecure_reset_token(now: int) -> str:
    # ANTI-PATTERN: deterministic PRNG (Mersenne Twister) seeded with a guessable value (the clock).
    rng = random.Random(now)
    return "%032x" % rng.getrandbits(128)


def attacker_recovers(token: str, around: int, window: int = 3600):
    # search space: attacker knows roughly when the token was issued and replays every candidate seed.
    for t in range(around - window, around + window + 1):
        if insecure_reset_token(t) == token:
            return t
    return None


if __name__ == "__main__":
    for name, value in secure_material().items():
        shown = value.hex() if isinstance(value, bytes) else value
        print(f"{name:18} {shown}")

    issued_at = int(time.time()) - 1234  # victim requested a reset ~20 min ago
    leaked = insecure_reset_token(issued_at)
    start = time.perf_counter()
    seed = attacker_recovers(leaked, around=int(time.time()))
    print("insecure token      ", leaked)
    print("attacker found seed ", seed, "== issued_at:", seed == issued_at,
          f"({time.perf_counter() - start:.3f}s)")
    print("attacker can mint   ", insecure_reset_token(seed) == leaked)
    print("same seed same token", insecure_reset_token(42) == insecure_reset_token(42))
    print("secrets differs     ", secrets.token_hex(16) != secrets.token_hex(16))
