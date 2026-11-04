"""Values for the CyberChef check: open Wycheproof aes_gcm tcId 10 by hand (AES Decrypt, GCM, tag + AAD)."""
import wycheproof_check as wc

t = next(t for g in wc.load("aes_gcm_subset.json")["testGroups"] for t in g["tests"] if t["tcId"] == 10)
for label, k in (("Key (hex)", "key"), ("IV (hex)", "iv"), ("Input = ct (hex)", "ct"), ("GCM Tag (hex)", "tag"), ("AAD (hex)", "aad")):
    print(f"{label:<18} {t[k]}")
print(f"{'expected output':<18} {t['msg']}")
print(f"{'truncated tag':<18} {t['tag'][:16]}  (8 bytes: the strict wrapper rejects it; see what CyberChef does)")
