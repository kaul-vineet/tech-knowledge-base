"""Try it: two small experiments on randomness (run: python try_it.py)."""
import secrets
import time

import randomness as lab

now = int(time.time())

# 1) Issue the clock-seeded token 2 hours ago: outside the attacker's +/-1 h window.
old = lab.insecure_reset_token(now - 7200)
print("1) token issued 2 h ago, window +/-1 h -> attacker finds:", lab.attacker_recovers(old, around=now))
print("   same token, window +/-3 h       -> attacker finds seed == issued_at:",
      lab.attacker_recovers(old, around=now, window=3 * 3600) == now - 7200)

# 2) Swap the PRNG for secrets: the same seed scan finds nothing.
token = secrets.token_hex(16)
print("2) secrets.token_hex(16) scanned over 7,201 seeds -> attacker finds:", lab.attacker_recovers(token, around=now))
