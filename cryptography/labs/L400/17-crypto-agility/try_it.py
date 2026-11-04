"""Try it: two experiments on crypto agility (run: python try_it.py)."""
import agile_envelope as ae
import agility_lint
import registry as reg

ring = ae.Keyring()
ring.add(reg.POLICY["aead_default"])
signers = {a: reg.new_signer(a) for a in reg.signing_algorithms()}
store = {f"d{i}": ae.seal(ring, ring.primary(), f"doc {i}".encode(), f"d{i}", signers) for i in range(10)}

# 1) Deprecate A256GCM (new default ChaCha20-Poly1305), migrate half the store lazily, then disallow A256GCM.
reg.POLICY["aead_default"] = "C20P1305"
ring.add("C20P1305")
reg.REGISTRY["A256GCM"].status = "deprecated"
for rid in sorted(store)[:5]:
    store[rid] = ae.migrate(ring, store[rid], signers)  # reads with the deprecated cipher, re-seals with the default
reg.REGISTRY["A256GCM"].status = "disallowed"
readable = []
for rid, env in sorted(store.items()):
    try:
        ae.open_(ring, env)
        readable.append(rid)
    except reg.DisallowedAlgorithm:
        pass
print(f"1) migrated 5/10, then disallowed A256GCM: {len(readable)}/10 readable; {ae.count_by_aead(store)}")

# 2) A developer "just" uses AES-GCM directly in an app module. Does the fitness function notice?
snippet = ("from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n"
           "def save(key, n, data):\n"
           "    return AESGCM(key).encrypt(n, data, b'')\n")
for file, line, why in agility_lint.scan_source(snippet, "orders/storage.py"):
    print(f"2) {file}:{line}: {why}")
