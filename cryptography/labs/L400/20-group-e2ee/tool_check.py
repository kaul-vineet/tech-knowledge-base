"""Fixed DEMO values for the CyberChef check: recompute one epoch secret with HKDF-SHA256 by hand.
epoch_secret = HKDF-SHA256(IKM = init_secret || commit_secret, salt = none, info = "kb-l20 epoch", L = 32)."""
import group_keys as gk

init_secret, commit_secret = bytes([0x11] * 32), bytes([0x22] * 32)  # demo values only
print("IKM (hex):      ", (init_secret + commit_secret).hex())
print("Salt:            (empty)")
print("Info (UTF8):     kb-l20 epoch")
print("Hash / length:   SHA256 / 32 bytes")
print("expected (hex): ", gk.kdf(init_secret + commit_secret, b"epoch").hex())
print("app key (info 'kb-l20 app' over that epoch secret):", gk.kdf(gk.kdf(init_secret + commit_secret, b"epoch"), b"app").hex())
