"""Build content/qbank/L100-L400.json for the cryptography topic (spec: kb/QBANK-SPEC.md).
Calculation answers are taken from research/qbank_checks.py CALC functions; 'What does this print?' answers are taken
from actually running the snippet. Answer positions are balanced per level with a seeded shuffle.
Run: python research/build_qbank.py  (then python research/qbank_checks.py and python ../tools/check_qbank.py cryptography)"""
import json
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qbank_checks as qc  # noqa: E402

TOPIC = Path(__file__).resolve().parent.parent
CALC = object()
BANK = {"L100": [], "L200": [], "L300": [], "L400": []}


def Q(level, num, lesson, qtype, diff, question, correct, wrong, expl, source, code=None):
    BANK[level].append(dict(num=num, lesson=lesson, type=qtype, difficulty=diff, question=question, correct=correct,
                            wrong=wrong, explanation=expl, source=source, code=code))


# ------------------------------------------------------------------ L100
L = "L100"
Q(L, 1, 1, "concept", 1, "The workbench script runs a known-answer test (KAT) after importing the library. What does the KAT prove that a successful import does not?",
  "The installed stack computes the published correct output",
  ["The library version matches the one pinned in requirements.txt", "The operating system's random generator is seeded", "The bundled OpenSSL is newer than version 3.0"],
  "A KAT compares real output with a published vector, so it proves the whole stack computes correctly. A version check only tells you what is installed, not that it works.",
  "Lesson 1 concepts / checkYourself")
Q(L, 2, 1, "concept", 2, "Two laptops both have `cryptography` installed, but only one reports argon2id_available True. What is the most likely reason?",
  "One has an older version or a build linked to OpenSSL older than 3.2",
  ["Argon2id is only enabled on x86_64 processors", "Argon2id needs administrator rights to reserve memory", "Argon2id needs a separately installed libsodium"],
  "Argon2id needs cryptography 44.0.0+ and an OpenSSL backend 3.2+; a source build against old OpenSSL or LibreSSL lacks it. CPU type and admin rights do not matter.",
  "Lesson 1 troubleshooting / checkYourself")
Q(L, 3, 1, "scenario", 1, "The workbench prints cryptography_pinned False. What is the right fix?",
  "Force-reinstall cryptography==50.0.2 inside the activated venv",
  ["Upgrade cryptography to the newest release system-wide with pip", "Delete __pycache__ folders and run the script again", "Set PYTHONHASHSEED=0 so results become reproducible"],
  "The check compares the running version with the pin, so reinstall the pinned version inside the venv. A system-wide upgrade changes a different interpreter and moves further from the pin.",
  "Lesson 1 troubleshooting")
Q(L, 4, 1, "scenario", 1, "On Windows, PowerShell says Activate.ps1 cannot be loaded when you activate the venv. What does the lesson recommend?",
  "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned, then reopen PowerShell",
  ["Set-ExecutionPolicy -Scope LocalMachine Unrestricted for every user on the PC", "Recreate the venv with --system-site-packages", "Rename Activate.ps1 to activate.bat and run it"],
  "Allowing RemoteSigned for the current user is the narrow fix. Making the whole machine Unrestricted also works but weakens the policy for every user and script.",
  "Lesson 1 troubleshooting")
Q(L, 5, 1, "concept", 1, "Why does the workbench pin one exact version of the crypto library?",
  "So APIs and results are reproducible across machines and over time",
  ["Because pinned packages run faster than unpinned ones", "Because newer crypto releases are usually less secure", "Because pinning turns off pip's hash checking"],
  "A pin means every learner runs the same API and gets the same outputs. It is about reproducibility, not speed, and newer releases are not less secure by default.",
  "Lesson 1 concepts")

Q(L, 6, 2, "concept", 1, "You change a single byte in a 10 MB file and hash it again with SHA-256. What happens to the digest?",
  "It changes completely and unpredictably",
  ["Only the last few hex characters change", "It stays the same because the change is tiny", "It grows by one byte to record the change"],
  "Hash functions are designed so any change gives an unrelated digest; that is how the lab's 1-byte change shows MISMATCH. A digest never 'mostly' matches or changes length.",
  "Lesson 2 concepts")
Q(L, 7, 2, "calculation", 2, "sha256_file reads a file in 64 KiB chunks. How many h.update() calls does it make for a file of exactly 1 GiB?",
  CALC, ["1,024 calls", "65,536 calls", "16,777,216 calls"],
  "1 GiB / 64 KiB = 2^30 / 2^16 = 16,384 chunks, so memory stays at about one chunk. 65,536 would be the chunk count for 16 KiB chunks.",
  "Lesson 2 concepts (streaming)")
Q(L, 8, 2, "concept", 2, "A download page lists a SHA-256 checksum next to the file. Why does this not stop a malicious mirror?",
  "The mirror can replace the file and the checksum, since anyone can compute SHA-256",
  ["SHA-256 collisions are cheap enough for mirrors to find", "Checksums only detect errors in files under 4 GB", "The checksum covers the file name but not the content"],
  "A plain hash has no key, so whoever serves the file can serve a matching hash. The issue is not collisions; get the checksum over a more trusted channel or use a MAC or signature.",
  "Lesson 2 checkYourself / caution")
Q(L, 9, 2, "concept", 1, "What does a valid HMAC-SHA256 tag prove that a plain SHA-256 digest does not?",
  "It was made by a holder of the secret key and the message is unchanged",
  ["The message is encrypted and hidden from eavesdroppers", "The message was sent at the time shown in its header", "The sender's identity is proven to any third party"],
  "HMAC adds a secret key, so only key holders can produce a valid tag. It gives integrity and authenticity, not confidentiality, and anyone holding the key could have made it.",
  "Lesson 2 overview / checkYourself")
Q(L, 10, 2, "code-reading", 1, "What does this print?",
  "64 False", ["32 False", "64 True", "32 True"],
  "hexdigest() returns 32 bytes as 64 hex characters, and different inputs give different digests. 32 is the byte length of digest(), not the length of the hex string.",
  "Lesson 2 code (sha256_text)",
  code='import hashlib\na = hashlib.sha256(b"report-v1").hexdigest()\nb = hashlib.sha256(b"report-v2").hexdigest()\nprint(len(a), a == b)')
Q(L, 11, 2, "debugging", 2, "This webhook check works in tests. What is the security problem?",
  "== can return early at the first differing byte; use hmac.compare_digest",
  ["== on bytes raises TypeError, so every request is rejected", "HMAC tags must be hex-decoded before any comparison", "== only compares the first 16 bytes of a 32-byte tag"],
  "Ordinary equality may stop at the first mismatch, leaking timing; compare_digest takes time independent of where they differ. == on bytes works and compares every byte, so tests pass.",
  "Lesson 2 concepts",
  code='import hashlib, hmac\n\ndef webhook_ok(key: bytes, body: bytes, tag: bytes) -> bool:\n    expected = hmac.new(key, body, hashlib.sha256).digest()\n    return tag == expected')
Q(L, 12, 2, "scenario", 2, "Your Python SHA-256 of a short text differs from the value you got with `echo text | sha256sum`. What is the most likely cause?",
  "echo added a trailing newline, so the tools hashed different bytes",
  ["sha256sum uses a different SHA-256 standard than Python's hashlib module", "Python hashes Unicode text as UTF-16 by default", "The shell truncated the digest to fit the terminal"],
  "echo appends \\n, so the tool hashed one extra byte; use printf or Set-Content -NoNewline. hashlib hashes whatever bytes you pass, and the code encodes text as UTF-8.",
  "Lesson 2 troubleshooting")
Q(L, 13, 2, "code-reading", 2, "What does this print?",
  "TypeError", ["True", "False", "ValueError"],
  "compare_digest needs two str (ASCII) or two bytes-like values; mixing hexdigest() and digest() raises TypeError. It does not quietly return False.",
  "Lesson 2 troubleshooting",
  code='import hashlib, hmac\nkey, msg = b"k" * 32, b"amount=10"\ntag = hmac.new(key, msg, hashlib.sha256)\ntry:\n    print(hmac.compare_digest(tag.hexdigest(), tag.digest()))\nexcept TypeError:\n    print("TypeError")')

Q(L, 14, 3, "concept", 1, "Which call is right for a password-reset token?",
  "secrets.token_urlsafe(32)",
  ["random.getrandbits(256) after random.seed()", "sha256(str(time.time())).hexdigest()", "random.choice over letters, 32 times"],
  "secrets reads the OS CSPRNG and is the module for tokens and keys. random is a deterministic Mersenne Twister, and hashing the time does not add unpredictability.",
  "Lesson 3 overview / concepts")
Q(L, 15, 3, "code-reading", 1, "What does this print?",
  "43 12", ["32 12", "44 12", "43 96"],
  "token_urlsafe(32) base64url-encodes 32 random bytes without padding, giving 43 characters; token_bytes(12) returns 12 bytes. 96 is the nonce size in bits, not bytes.",
  "Lesson 3 code (secure_material)",
  code="import secrets\nprint(len(secrets.token_urlsafe(32)), len(secrets.token_bytes(12)))")
Q(L, 16, 3, "calculation", 2, "attacker_recovers() tries every whole-second seed from around - 3600 to around + 3600 inclusive. At most how many seeds does it test?",
  CALC, ["3,600 seeds", "7,200 seeds", "86,400 seeds"],
  "range(around - 3600, around + 3600 + 1) has 7,201 values, which a laptop checks in under a second. 7,200 forgets that both ends are included.",
  "Lesson 3 code / expectedResults")
Q(L, 17, 3, "concept", 2, "A developer makes a reset token with sha256(str(time.time())). Why is it still insecure?",
  "The attacker hashes every candidate time too; the search space stays tiny",
  ["SHA-256 can be reversed to recover the timestamp", "The token is too short to be stored safely", "time.time() repeats every 24 hours"],
  "Hashing a guessable input leaves only a few thousand candidates, so the attacker hashes each guess and compares. SHA-256 is not reversed; it is simply bypassed by guessing.",
  "Lesson 3 checkYourself")
Q(L, 18, 3, "scenario", 1, "A team writes a traffic simulation that must replay exactly the same run in tests. Which generator should it use?",
  "random with a fixed seed, because predictability is a feature here",
  ["secrets, because every random value should be secure", "os.urandom, reseeded before every simulation step", "secrets.SystemRandom with a fixed seed for replay"],
  "For simulations, games and reproducible tests random is the right tool. secrets and SystemRandom cannot be seeded to replay, and they are only needed for security values.",
  "Lesson 3 checkYourself / troubleshooting")
Q(L, 19, 3, "code-reading", 1, "What does this print?",
  "True", ["False", "It differs from run to run", "TypeError"],
  "random.Random is deterministic: the same seed gives the same sequence, which is why a guessable seed (like the clock) lets an attacker regenerate values.",
  "Lesson 3 concepts",
  code="import random\na = random.Random(1730000000).getrandbits(64)\nb = random.Random(1730000000).getrandbits(64)\nprint(a == b)")
Q(L, 20, 3, "debugging", 2, "A code review flags this AES-GCM helper. What should change?",
  "Use secrets.token_bytes(12) or os.urandom(12) for the nonce",
  ["Use random.randbytes(16), since AES-GCM always needs 16-byte nonces", "Call random.seed() once at start-up to mix in entropy", "Use random.randbytes(12) but hash the result first"],
  "Nonces and keys must come from the OS CSPRNG; random is predictable and can repeat across runs. Hashing or reseeding a predictable generator does not make it secure.",
  "Lesson 3 concepts / caution",
  code="import random\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\n\ndef seal(key: bytes, msg: bytes) -> bytes:\n    nonce = random.randbytes(12)\n    return nonce + AESGCM(key).encrypt(nonce, msg, None)")
Q(L, 21, 3, "concept", 1, "Why must security values never come from a PRNG seeded with a user ID or process ID?",
  "Anyone who guesses the seed can regenerate every value it produced",
  ["Seeding with an ID makes the generator raise errors", "User IDs are too long to be used as seeds", "The values become unique per user, which leaks each user's identity"],
  "A deterministic PRNG is fully determined by its seed, and IDs are easy to guess. The problem is predictability, not errors or length.",
  "Lesson 3 concepts / caution")

Q(L, 22, 4, "calculation", 1, "seal() stores a fresh 12-byte nonce in front of AES-256-GCM output. How long is the stored blob for a 100-byte plaintext?",
  CALC, ["100 bytes", "116 bytes", "112 bytes"],
  "AEAD output is ciphertext (same length as plaintext) plus a 16-byte tag, and the 12-byte nonce is stored in front: 12 + 100 + 16. 116 forgets the nonce.",
  "Lesson 4 concepts")
Q(L, 23, 4, "calculation", 2, "One key encrypts 2^32 messages with random 96-bit nonces. Using the birthday approximation n^2/2 / 2^96, what is the chance that any two nonces collide?",
  CALC, ["about 2^-64", "about 2^-1", "about 2^-96"],
  "2^32 * 2^32 / 2 / 2^96 = 2^-33, which is why about 2^32 messages per key is the usual limit. 2^-64 ignores that every pair of messages can collide.",
  "Lesson 4 concepts (2^32 guidance)")
Q(L, 24, 4, "calculation", 2, "Roughly how many random 96-bit nonces under one key give a 50 % chance of a collision?",
  CALC, ["about 2^96", "about 2^32", "about 2^64"],
  "Collisions become likely near the square root of the space: sqrt(2 ln 2 * 2^96) is about 2^48. The 2^32 guidance is far below this to keep the risk negligible.",
  "Lesson 4 concepts (2^32 guidance)")
Q(L, 25, 4, "concept", 2, "Two messages were encrypted with AES-GCM under the same key and the same nonce. What does an eavesdropper gain?",
  "The XOR of the two plaintexts, and the ability to forge GCM tags",
  ["Nothing, because each ciphertext still carries its own 16-byte tag", "The AES key directly, from a single ciphertext", "Only the lengths, which AEAD never hides anyway"],
  "Same key and nonce means the same keystream, so XOR of ciphertexts equals XOR of plaintexts, and GCM authenticity breaks too. The tags do not prevent this.",
  "Lesson 4 concepts / checkYourself")
Q(L, 26, 4, "scenario", 2, "A row stores an encrypted address and a readable user_id. You want decryption to fail if someone copies the ciphertext to another user's row. Where does user_id go?",
  "In the AAD: readable, but bound to the ciphertext",
  ["Inside the plaintext, encrypted together with the address", "Appended to the nonce before encrypting", "Hashed into the key with SHA-256"],
  "AAD is authenticated but not encrypted, so a moved ciphertext fails with InvalidTag. Putting it in the plaintext hides it but does not stop the row swap from decrypting.",
  "Lesson 4 checkYourself")
Q(L, 27, 4, "code-reading", 1, "What does this print?",
  "InvalidTag", ["b'balance=100'", "b''", "ValueError"],
  "The AAD is part of the authentication, so decrypting with user=8 instead of user=7 raises InvalidTag; AEAD never returns plaintext from a failed check.",
  "Lesson 4 concepts",
  code='import os\nfrom cryptography.exceptions import InvalidTag\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\ng, n = AESGCM(AESGCM.generate_key(bit_length=256)), os.urandom(12)\nct = g.encrypt(n, b"balance=100", b"user=7")\ntry:\n    print(g.decrypt(n, ct, b"user=8"))\nexcept InvalidTag:\n    print("InvalidTag")')
Q(L, 28, 4, "debugging", 2, "This helper encrypts every message correctly and every test passes. What is wrong?",
  "Every message reuses the same (key, nonce) pair",
  ["AES-256-GCM needs a 16-byte nonce, not 12 bytes", "AAD cannot be None for AES-GCM", "The nonce must be kept secret, not prepended"],
  "A constant nonce under one key repeats the keystream, leaking XORs of plaintexts and breaking GCM authenticity. 12 bytes is the right size and nonces are public.",
  "Lesson 4 caution",
  code="from cryptography.hazmat.primitives.ciphers.aead import AESGCM\nNONCE = bytes(12)\n\ndef seal(key: bytes, msg: bytes) -> bytes:\n    return NONCE + AESGCM(key).encrypt(NONCE, msg, None)")
Q(L, 29, 4, "debugging", 2, "Blobs are stored as nonce (12 bytes) || ciphertext || tag. Why does every decrypt fail with InvalidTag?",
  "It slices 16 bytes as the nonce, so nonce and ciphertext are both wrong",
  ["AESGCM.decrypt expects the tag first, then the ciphertext", "The key must be regenerated with generate_key() before every decrypt call", "AAD must be b'' rather than None to match encryption"],
  "Decryption needs exactly the nonce, key and AAD used to encrypt; slicing at 16 moves 4 ciphertext bytes into the nonce. The tag is at the end and None AAD matches None.",
  "Lesson 4 troubleshooting",
  code="from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n\ndef open_(key: bytes, blob: bytes) -> bytes:\n    return AESGCM(key).decrypt(blob[:16], blob[16:], None)")

Q(L, 30, 5, "concept", 1, "Why is a plain SHA-256 of the password a bad way to store it?",
  "SHA-256 is fast, so attackers test billions of guesses per second",
  ["SHA-256 output is too short to store safely", "SHA-256 can be decrypted with the server's key", "SHA-256 gives different output on different CPUs"],
  "Password hashing must be slow, memory-hard and salted so each guess is costly. SHA-256 is one-way but built for speed, which helps the attacker.",
  "Lesson 5 concepts")
Q(L, 31, 5, "calculation", 1, "The lab's Argon2id parameters use memory_cost=19456, which pyca/cryptography counts in KiB. How much memory is that?",
  CALC, ["19,456 MiB", "1.9 MiB", "190 MiB"],
  "19456 KiB / 1024 = 19 MiB, the OWASP minimum row (m=19 MiB, t=2, p=1). Reading the number as MiB would demand about 19 GiB.",
  "Lesson 5 concepts / code")
Q(L, 32, 5, "calculation", 2, "scrypt needs about 128 * N * r bytes of memory. How much does the OWASP fallback N=2^17, r=8 use?",
  CALC, ["16 MiB", "1,024 MiB", "1 MiB"],
  "128 * 131072 * 8 bytes = 134,217,728 bytes = 128 MiB, which is why low-RAM boxes hit MemoryError. 16 MiB forgets the factor 8 for r.",
  "Lesson 5 code / troubleshooting")
Q(L, 33, 5, "calculation", 2, "An attacker tries 10 million candidate passwords against one stolen hash. Their rig does 10^10 SHA-256 guesses/s but only 10^4 Argon2id guesses/s. How long per user for SHA-256 vs Argon2id?",
  CALC, ["1 s vs 1 s", "0.0001 s vs 100 s", "10 s vs 1000 s"],
  "10^7 / 10^10 = 0.001 s and 10^7 / 10^4 = 1000 s: the slow hash multiplies the attacker's cost per guess. The defender pays that cost only once per login.",
  "Lesson 5 checkYourself")
Q(L, 34, 5, "code-reading", 1, "What does this print?",
  "argon2id m=19456,t=2,p=1", ["argon2id v=19", "v=19 m=19456,t=2,p=1", "argon2id MDEyMzQ1Njc4OWFiY2RlZg"],
  "The PHC string is $alg$version$params$salt$hash; splitting on $ gives an empty first field, so alg is argon2id and params is m=19456,t=2,p=1. This is how verify reads parameters back.",
  "Lesson 5 code (PHC string)",
  code='stored = "$argon2id$v=19$m=19456,t=2,p=1$MDEyMzQ1Njc4OWFiY2RlZg$nUxirfVK2I/vOT6f2ly2wSgjwZ1oqwTLCmrcpDyjicA"\n_, alg, ver, params, salt, digest = stored.split("$")\nprint(alg, params)')
Q(L, 35, 5, "scenario", 1, "Two users both choose the password hunter2. Why are their stored Argon2id strings different?",
  "Each hash uses its own random salt",
  ["Argon2id adds the current time to each hash", "Argon2id output is random even for equal inputs", "The username is mixed in as the secret key"],
  "A unique salt per password makes outputs unrelated, so equal passwords are not visible and precomputed tables fail. With the same salt and parameters Argon2id is deterministic.",
  "Lesson 5 checkYourself")
Q(L, 36, 5, "scenario", 2, "Logins take more than 1 s under load with your Argon2id settings. What should you do?",
  "Benchmark and pick an equivalent lower-memory OWASP row, not below the minimum",
  ["Switch to SHA-256 with a per-user salt", "Cache each verified password in memory for an hour", "Lower settings to m=4 MiB, t=1 to cut the cost"],
  "OWASP lists equivalent rows that trade memory for iterations; stay at or above the minimum. Fast salted SHA-256 or a cache of plaintext passwords throws away the protection.",
  "Lesson 5 troubleshooting")
Q(L, 37, 5, "debugging", 2, "This function is used for every user. What is the weakness?",
  "One fixed salt for everyone: equal passwords give equal hashes",
  ["Argon2id rejects salts that are written as text", "length=32 is too short for a password hash", "The PHC string leaks the password length"],
  "A salt must be unique and random per password (16 bytes, os.urandom); a shared salt lets an attacker attack all users at once. A 32-byte output is fine.",
  "Lesson 5 code / checkYourself",
  code='from cryptography.hazmat.primitives.kdf.argon2 import Argon2id\nSALT = b"static-app-salt!"\n\ndef hash_password(pw: str) -> str:\n    kdf = Argon2id(salt=SALT, length=32, iterations=2, lanes=1, memory_cost=19456)\n    return kdf.derive_phc_encoded(pw.encode())')

Q(L, 38, 6, "concept", 1, "A config file stores db_password as base64. What protection does that give?",
  "None: anyone can decode it without a key",
  ["Weak encryption that stops casual readers", "One-way protection like a hash", "Integrity: edits are detected on decode"],
  "Base encoding changes representation only and gives no confidentiality (RFC 4648 §12). It is reversible by anyone and detects no edits.",
  "Lesson 6 concepts / caution")
Q(L, 39, 6, "calculation", 1, "How many characters does standard base64 (with padding) produce for a 32-byte key?",
  CALC, ["32 characters", "43 characters", "64 characters"],
  "Base64 encodes each 3 bytes as 4 characters and pads the last group: ceil(32/3)*4 = 44. 43 is the unpadded base64url length used by token_urlsafe.",
  "Lesson 6 code (encode)")
Q(L, 40, 6, "code-reading", 1, "What does this print?",
  "Zm9vYmFy 666f6f626172", ["Zm9vYmFy 0x666f6f626172", "Zm9vYmFyCg== 666f6f626172", "666f6f626172 Zm9vYmFy"],
  "base64('foobar') is Zm9vYmFy (RFC 4648), and bytes.hex() gives plain lowercase hex. It adds no 0x prefix, and no newline is encoded because none was in the input.",
  "Lesson 6 expectedResults",
  code='import base64\nprint(base64.b64encode(b"foobar").decode(), b"foobar".hex())')
Q(L, 41, 6, "concept", 1, "Why can't you 'decrypt' a SHA-256 digest back to its input?",
  "Hashing is one-way: there is no key and no inverse",
  ["The key is discarded right after hashing, so nobody has it", "Only the OS hashing tool can reverse it", "It needs the salt, which is never stored"],
  "A hash has no key and no inverse function; the only option is to guess inputs and compare digests. Encryption is the reversible tool.",
  "Lesson 6 checkYourself")
Q(L, 42, 6, "scenario", 1, "A home address must be shown on the user's profile page and protected at rest. Which tool fits?",
  "AEAD encryption, because the value must come back",
  ["SHA-256, because it is irreversible and fast to compute", "Base64, because it hides the text", "Argon2id, because it is memory-hard"],
  "Only encryption is reversible with a key, so the address can be displayed again. A hash or Argon2id output cannot be turned back into the address.",
  "Lesson 6 checkYourself")
Q(L, 43, 6, "scenario", 2, "A file service wants to detect when a user uploads a file it already stores, without keeping a second copy. Which tool fits?",
  "A SHA-256 fingerprint of each file",
  ["AES-GCM encryption of each file with a random nonce", "Base64 encoding of each file", "A random token per file"],
  "Hashing is for comparing and fingerprinting: equal files give equal digests. AES-GCM with random nonces gives different outputs for the same file, so it cannot find duplicates.",
  "Lesson 6 concepts")
Q(L, 44, 6, "debugging", 2, "Decoding the middle part of a JWT-style token raises binascii.Error: Incorrect padding. What is the fix?",
  "Use urlsafe_b64decode and add back the stripped = padding",
  ["Decrypt the segment first; it is encrypted", "Strip the final character and retry b64decode", "Hash the segment, since it is a digest"],
  "Token segments are base64url without padding, so restore padding and use the URL-safe alphabet. The segment is only encoded, not encrypted or hashed.",
  "Lesson 6 troubleshooting",
  code='import base64\nseg = "eyJzdWIiOiJhbGljZSJ9"[:-1]  # base64url, padding removed\nbase64.b64decode(seg)')
Q(L, 45, 6, "code-reading", 2, "What does this print?",
  "True False", ["True True", "False False", "False True"],
  "Hashing is deterministic, so equal inputs give equal digests. AEAD with a fresh random nonce is randomised, so encrypting the same data twice gives different blobs.",
  "Lesson 6 expectedResults",
  code='import hashlib, os\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\nkey = AESGCM.generate_key(bit_length=256)\ndef enc(d):\n    n = os.urandom(12)\n    return n + AESGCM(key).encrypt(n, d, None)\nsame_hash = hashlib.sha256(b"x").digest() == hashlib.sha256(b"x").digest()\nprint(same_hash, enc(b"x") == enc(b"x"))')

# ------------------------------------------------------------------ L200
L = "L200"
Q(L, 1, 7, "concept", 2, "Why is it safe to publish release.pub on the project website?",
  "Verifying needs only the public key; signing needs the private key",
  ["The public key is encrypted with the private key", "Ed25519 public keys expire after one release", "Verifiers must also hold a shared secret, so the public key alone is useless"],
  "Signatures use a key pair: the private key signs and the public key only verifies, with no shared secret. Publishing the public key lets anyone verify but nobody sign.",
  "Lesson 7 concepts / checkYourself")
Q(L, 2, 7, "concept", 2, "You sign the same file twice with the same Ed25519 key and get identical signatures. What does this mean?",
  "Nothing is wrong: Ed25519 signatures are deterministic",
  ["The random generator is broken and must be reseeded", "The second signature reused a nonce and so leaks the private key", "The file was not read, so an empty input was signed"],
  "RFC 8032 Ed25519 derives its per-signature value from the key and message, so equal inputs give equal signatures. Nonce-reuse worries apply to randomised schemes like ECDSA.",
  "Lesson 7 checkYourself")
Q(L, 3, 7, "calculation", 2, "What are the raw sizes of an Ed25519 private key, public key and signature?",
  CALC, ["private 64 B, public 32 B, signature 64 B", "private 32 B, public 64 B, signature 32 B", "private 32 B, public 32 B, signature 32 B"],
  "Ed25519 uses 32-byte keys and 64-byte signatures. The 64-byte private size comes from formats that store seed and public key together.",
  "Lesson 7 concepts / expectedResults")
Q(L, 4, 7, "calculation", 2, "The lab saves the Ed25519 private key as PEM (PKCS#8, unencrypted) and the public key as PEM (SubjectPublicKeyInfo). How large are the two files?",
  CALC, ["private 32 B, public 32 B", "private 113 B, public 119 B", "private 64 B, public 44 B"],
  "PEM adds an ASN.1 wrapper, base64 and header lines around the 32 raw bytes: 119 B private and 113 B public. 44 B is the DER public key without PEM armour.",
  "Lesson 7 expectedResults")
Q(L, 5, 7, "code-reading", 2, "What does this print?",
  "InvalidSignature", ["valid", "ValueError", "valid (with a warning)"],
  "The signature covers every byte; changing 's' to 'z' makes verify() raise InvalidSignature. Verification never returns a 'nearly valid' result.",
  "Lesson 7 concepts",
  code='from cryptography.exceptions import InvalidSignature\nfrom cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey\nk = Ed25519PrivateKey.generate()\nsig = k.sign(b"app-1.0.tar.gz bytes")\ntry:\n    k.public_key().verify(sig, b"app-1.0.tar.gz bytez")\n    print("valid")\nexcept InvalidSignature:\n    print("InvalidSignature")')
Q(L, 6, 7, "debugging", 2, "release.pub is a PEM file. Why does this raise ValueError?",
  "from_public_bytes wants 32 raw bytes; use load_pem_public_key for PEM",
  ["The file must be opened in text mode for PEM", "Ed25519 public keys must be base64-decoded twice", "The private key is needed to load a public key"],
  "PEM and raw formats are different: from_public_bytes takes exactly 32 raw bytes, while a PEM file needs serialization.load_pem_public_key. Text mode would make things worse.",
  "Lesson 7 troubleshooting",
  code='from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey\nwith open("release.pub", "rb") as f:\n    pub = Ed25519PublicKey.from_public_bytes(f.read())')
Q(L, 7, 7, "scenario", 2, "Release signatures verify on macOS and Linux but fail only on Windows. What is the most likely cause?",
  "Files are read or written in text mode, which changes line endings",
  ["Windows uses a different Ed25519 curve", "Windows needs the signature in PEM form, not as 64 raw bytes on disk", "Windows clocks make signatures expire early"],
  "Text mode on Windows translates line endings, so the verified bytes differ from the signed bytes; use 'rb'/'wb'. Ed25519 is the same everywhere and signatures do not expire.",
  "Lesson 7 troubleshooting")
Q(L, 8, 7, "scenario", 2, "A CI job signs releases and thousands of users verify them. Where should each key live?",
  "Private key in CI secrets or an HSM; public key shipped with the installer",
  ["Both keys committed to the repo so builds are reproducible", "Private key shipped with the installer so users can re-sign", "Public key kept secret in CI; private key published so that anyone can audit releases"],
  "Only the signer needs the private key, so keep it in a protected store; verifiers only need the public key. Committing or shipping the private key lets anyone sign.",
  "Lesson 7 caution / L300 lesson 14 caution")

Q(L, 9, 8, "calculation", 2, "seal() returns ephemeral public key || ChaCha20-Poly1305 ciphertext with tag. How long is the blob for the 29-byte message 'db password rotation at 02:00'?",
  CALC, ["61 bytes", "45 bytes", "89 bytes"],
  "32 bytes of ephemeral X25519 public key + 29 bytes of ciphertext + 16-byte tag = 77; the zero nonce is not stored. 89 wrongly adds a 12-byte nonce.",
  "Lesson 8 expectedResults")
Q(L, 10, 8, "code-reading", 2, "Using the RFC 7748 §6.1 test keys, what does this print?",
  "4a5d9d5b", ["8520f009", "de9edb7d", "00000000"],
  "X25519(a, B) gives the shared secret K = 4a5d9d5b... from the RFC. 8520f009 and de9edb7d are the start of Alice's and Bob's public keys, not the secret.",
  "Lesson 8 code (RFC 7748 vector)",
  code='from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey\na = X25519PrivateKey.from_private_bytes(bytes.fromhex(\n    "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"))\nB = X25519PublicKey.from_public_bytes(bytes.fromhex(\n    "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"))\nprint(a.exchange(B)[:4].hex())')
Q(L, 11, 8, "concept", 2, "Why does seal_box run the X25519 output through HKDF instead of using it as the AEAD key?",
  "The raw DH output is not a uniform key; HKDF derives one bound to context",
  ["X25519 outputs 64 bytes and the AEAD needs 32", "HKDF encrypts the shared secret for transport", "HKDF makes the exchange quantum-resistant"],
  "A KDF turns the shared secret into a proper key and binds it to the salt (both public keys) and info label. X25519 already outputs 32 bytes, and HKDF adds no quantum resistance.",
  "Lesson 8 concepts")
Q(L, 12, 8, "concept", 2, "Lesson 4 forbids fixed nonces, yet seal_box uses an all-zero nonce. Why is that safe here?",
  "Each message gets a fresh derived key, so (key, nonce) never repeats",
  ["ChaCha20-Poly1305 does not use its nonce input", "The 16-byte tag protects against nonce reuse", "HKDF scrambles the nonce before encryption"],
  "The danger is reusing a (key, nonce) pair; a new ephemeral key per message gives a new key every time. Tags do not prevent damage from nonce reuse.",
  "Lesson 8 concepts / checkYourself")
Q(L, 13, 8, "concept", 2, "Bob opens a sealed message with his private key. What does that tell him about the sender?",
  "Nothing: anyone with his public key could have sealed it",
  ["It came from whoever holds the ephemeral private key on file", "It came from someone in his contact list", "It came from Alice, because X25519 authenticates both sides"],
  "Sealing only needs Bob's public key, so it gives confidentiality, not sender authentication; add a signature for that. The ephemeral key is thrown away and identifies nobody.",
  "Lesson 8 checkYourself")
Q(L, 14, 8, "concept", 2, "Opening a message raises ValueError: Error computing shared key. What does this tell you?",
  "The peer public key is a small-order point (e.g. all zeros); reject the message",
  ["Bob's private key file is corrupt and must be regenerated", "The HKDF info label differs between sender and receiver", "The ciphertext was truncated in transit"],
  "An all-zero or small-order public key gives a zero shared secret, which the library and lab refuse. A wrong info label shows up later as InvalidTag, not at the exchange.",
  "Lesson 8 troubleshooting")
Q(L, 15, 8, "debugging", 2, "The sender and receiver were updated separately. Why does the right recipient now get InvalidTag?",
  "The two sides use different HKDF info labels, so they derive different keys",
  ["The receiver must use the sender's private key", "HKDF salt must be random, not the public keys", "ChaCha20-Poly1305 cannot decrypt with a zero nonce"],
  "Both sides must derive the key with the same salt and INFO label; any difference gives a different key and InvalidTag. Binding the public keys as salt is deliberate.",
  "Lesson 8 troubleshooting",
  code='# sender (old build)\nINFO = b"kb-crypto-l200/v1/X25519"\n# receiver (new build)\nINFO = b"kb-crypto-l200/v2/X25519"\n# both: HKDF(SHA256(), 32, salt=eph_pub + rcpt_pub, info=INFO).derive(shared)')
Q(L, 16, 8, "scenario", 2, "To save CPU, a sender generates one ephemeral key at start-up and reuses it for every message, still with the zero nonce. What breaks?",
  "Messages to the same recipient reuse one (key, nonce) pair",
  ["Nothing, because HKDF output differs per message", "Only performance, since key generation is cheap anyway in X25519", "Only forward secrecy for the sender's long-term key"],
  "Same ephemeral key and same recipient give the same derived key, and the nonce is fixed, so the nonce-reuse failures from lesson 4 return. HKDF inputs are identical, so its output is too.",
  "Lesson 8 concepts")

Q(L, 17, 9, "concept", 2, "What is a certificate, at its core?",
  "The CA's signature over a name, a public key, validity dates and usage",
  ["An encrypted copy of the server's private key", "A random token the CA issues to each server", "A hash of the server's private key and hostname"],
  "A certificate binds a name and public key with dates and usage, signed by the issuer. It never contains the private key.",
  "Lesson 9 concepts")
Q(L, 18, 9, "scenario", 2, "A certificate has CN=api.local but its SAN lists only localhost. A client connects to api.local. What happens?",
  "Verification fails: verifiers match the hostname against the SAN",
  ["It verifies, because the CN matches the hostname being dialled", "It verifies, because SAN entries are only hints", "It verifies with a warning about the CN"],
  "Modern verifiers match names against the SAN extension and ignore the CN. Matching the CN is a legacy behaviour.",
  "Lesson 9 concepts / checkYourself")
Q(L, 19, 9, "concept", 2, "Path validation checks more than signatures. Which list matches the lesson?",
  "Signatures, dates, extensions and name, against a trust store",
  ["Signatures only, since dates and names are checked by the server", "The leaf's signature and its key size only", "Name and dates; signatures are checked by DNS"],
  "A chain is valid only if every signature verifies, every certificate is in date, extensions such as BasicConstraints and KeyUsage fit, and the name matches.",
  "Lesson 9 concepts")
Q(L, 20, 9, "debugging", 2, "Building a chain to the lab root fails with 'Certificate is missing required extension'. What is the fix?",
  "Add a critical KeyUsage extension to the CA certificate",
  ["Remove BasicConstraints from the CA certificate so it can sign leaves", "Add the root certificate's SAN to the leaf", "Make the leaf certificate's validity longer"],
  "The verifier's profile requires a CA certificate with KeyUsage (keyCertSign) marked critical. Removing BasicConstraints would make the CA invalid instead.",
  "Lesson 9 troubleshooting")
Q(L, 21, 9, "scenario", 2, "A brand-new certificate fails with 'cert is not valid at validation time'. What is the likely cause?",
  "The checking machine's clock is behind not_valid_before",
  ["The CA used the wrong signature hash", "The certificate has already expired and must be reissued by the CA", "The SAN contains an IP address"],
  "A new cert fails this way when the verifier's clock is earlier than notBefore; fix NTP or backdate notBefore a few minutes. An expiry problem needs an old certificate.",
  "Lesson 9 troubleshooting")
Q(L, 22, 9, "calculation", 2, "The lab's leaf is valid from 2026-10-28 to 2026-11-27. How long is its lifetime?",
  CALC, ["31 days", "28 days", "1 month and 1 day"],
  "Subtracting the dates gives 30 days (October has 31 days, so 28 Oct + 30 days = 27 Nov). A short lifetime limits damage from a leaked key.",
  "Lesson 9 expectedResults")
Q(L, 23, 9, "code-reading", 2, "A simplified diagnose() from the lab classifies a time check. What does this print?",
  "NOT_YET_VALID", ["EXPIRED", "OK", "None"],
  "The check time (100) is before notBefore (105), so the first branch returns NOT_YET_VALID; code decides the label, which is why a clock-skew case is not EXPIRED.",
  "Lesson 9 checkYourself",
  code='def diagnose(now, not_before, not_after):\n    if now < not_before:\n        return "NOT_YET_VALID"\n    if now > not_after:\n        return "EXPIRED"\n    return "OK"\n\nprint(diagnose(100, 105, 200))')
Q(L, 24, 9, "debugging", 2, "The root (path_length=1) signs an intermediate (path_length=0) that issues the localhost leaf. Verification with only the root in the trust store fails. What is the fix?",
  "Pass the intermediate in intermediates= so the chain can be built",
  ["Set ca=True in the leaf's BasicConstraints so it can chain itself", "Raise the intermediate's path_length to 1", "Copy the root's subject into the leaf"],
  "The verifier needs the intermediate certificate to link leaf to root; it is passed as an untrusted intermediate. Marking the leaf as a CA would make it an invalid end-entity certificate.",
  "Lesson 9 buildTask (intermediate CA)")

Q(L, 25, 10, "concept", 2, "What does ssl.create_default_context(cafile='pki/ca.pem') give a client?",
  "CERT_REQUIRED and hostname checking against the lab CA",
  ["Encryption only, with no certificate checks", "Certificate checks but no hostname check", "Trust in every CA on the system plus the lab CA, with no name check"],
  "The default client context requires a valid certificate and checks the hostname; cafile replaces the default trust store. Turning either check off is the common misconfiguration.",
  "Lesson 10 concepts")
Q(L, 26, 10, "concept", 2, "In wrap_socket(sock, server_hostname='localhost'), what is server_hostname used for?",
  "It is sent as SNI and is the name checked against the certificate's SAN",
  ["Only to choose which network interface to dial", "Only for logging; the IP address is verified instead", "To pick the client certificate to send"],
  "server_hostname is both the SNI value and the identity the client verifies. The dialled IP is not what gets checked.",
  "Lesson 10 concepts")
Q(L, 27, 10, "concept", 2, "The client dials 127.0.0.1 with server_hostname='localhost'. Which SAN entry must match?",
  "DNS:localhost",
  ["IP:127.0.0.1", "Either one; the client tries both", "The certificate's CN"],
  "The name checked is server_hostname, not the address dialled, so DNS:localhost counts. The IP entry would matter only if server_hostname were '127.0.0.1'.",
  "Lesson 10 checkYourself")
Q(L, 28, 10, "concept", 2, "A client keeps CERT_REQUIRED but sets check_hostname=False. Why is that dangerous?",
  "Any certificate from a trusted CA, for any site, is accepted",
  ["Every handshake now fails with a hostname verification error instead", "The connection falls back to plaintext", "Only expired certificates are accepted"],
  "Without the name check the client proves only that someone has a trusted certificate, not that it is the right server. Handshakes still succeed, which is why it is easy to miss.",
  "Lesson 10 checkYourself")
Q(L, 29, 10, "debugging", 2, "A test client gets CERTIFICATE_VERIFY_FAILED against your local TLS server. What is the right fix?",
  "Pass the lab CA: verify='pki/ca.pem'",
  ["Pass verify=False in the test client", "Set check_hostname=False in the test client", "Add the server's private key to the client"],
  "The client does not trust the lab CA yet, so give it that CA file (or REQUESTS_CA_BUNDLE). verify=False silences all checks and hides real attacks.",
  "Lesson 10 troubleshooting",
  code='import requests\nr = requests.get("https://localhost:8443/health")\n# ssl.SSLCertVerificationError: CERTIFICATE_VERIFY_FAILED')
Q(L, 30, 10, "code-reading", 2, "What does this print?",
  "True True", ["False False", "True False", "False True"],
  "create_default_context() builds a client context with verify_mode CERT_REQUIRED and check_hostname True. Only server-side contexts default to not checking peers.",
  "Lesson 10 concepts",
  code="import ssl\nctx = ssl.create_default_context()\nprint(ctx.verify_mode == ssl.CERT_REQUIRED, ctx.check_hostname)")
Q(L, 31, 10, "scenario", 2, "A client is REFUSED with verify_code=20: unable to get local issuer certificate. Which misconfiguration is it?",
  "The client does not trust the CA that issued the server certificate",
  ["The hostname does not match any of the DNS entries in the certificate's SAN", "The server certificate has expired", "The client requested TLS 1.2 instead of 1.3"],
  "Code 20 means the chain cannot reach a trusted root, so the CA file is wrong or missing. A hostname mismatch is code 62.",
  "Lesson 10 expectedResults")
Q(L, 32, 10, "concept", 2, "When certificate verification fails, what has the client sent to the server?",
  "No application data: the handshake aborts first",
  ["The request, but the server's response is discarded", "The request headers but not the body", "Everything, encrypted with a fallback key"],
  "TLS verifies before the handshake completes, so the connection fails closed before any data. That is why a refused connection never leaks the request.",
  "Lesson 10 concepts")
Q(L, 33, 10, "design", 2, "You extend the TLS server to require client certificates (mTLS). What must the server's context do?",
  "Set verify_mode=CERT_REQUIRED and load the CA that issues client certs",
  ["Set check_hostname=True and load the server key twice", "Use the client's private key as the server key", "Accept any client cert and check its CN later"],
  "A server only asks for and verifies client certificates when verify_mode is CERT_REQUIRED and it trusts the client CA. Checking a name after accepting any cert skips path validation.",
  "Lesson 10 overview (mTLS)")

Q(L, 34, 11, "concept", 2, "Who decides which algorithm is used to verify a token?",
  "The verifier, from its own allow-list with one key per algorithm",
  ["The token header, since the issuer chose it", "Whichever algorithm verifies first", "The client, through a request parameter"],
  "The header is attacker-controlled, so trusting it enables alg 'none' and key confusion. The verifier keeps its own algorithm-to-key list.",
  "Lesson 11 concepts")
Q(L, 35, 11, "code-reading", 2, "What does this print?",
  "user", ["KeyError", "InvalidSignature", "b'c2ln'"],
  "The payload is only base64url-encoded, so anyone can read the claims without a key. Signed is not encrypted; never put secrets in claims.",
  "Lesson 11 concepts",
  code='import base64, json\ndef b64u(d):\n    return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()\ntok = b64u({"alg": "EdDSA"}) + "." + b64u({"sub": "alice", "role": "user"}) + ".c2ln"\np = tok.split(".")[1]\nprint(json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))["role"])')
Q(L, 36, 11, "calculation", 2, "How many characters is the third (signature) segment of an EdDSA token, base64url-encoded without padding?",
  CALC, ["64 characters", "88 characters", "43 characters"],
  "A 64-byte Ed25519 signature is 512 bits; base64url uses 6 bits per character, so ceil(512/6) = 86. 88 would include the two padding characters.",
  "Lesson 11 code (sign, b64u)")
Q(L, 37, 11, "scenario", 2, "Five internal APIs verify tokens that one issuer creates. Why is HS256 risky here?",
  "Every API holds the secret, so any of them could mint tokens",
  ["HS256 tags are too short to resist brute-force forgery by an API", "HS256 cannot carry exp or aud claims", "HS256 tokens can only be verified once"],
  "HMAC is symmetric, so every verifier can also sign; one compromised API can forge tokens for all. With EdDSA only the issuer holds the private key.",
  "Lesson 11 checkYourself")
Q(L, 38, 11, "scenario", 2, "A token's header says EdDSA, but the verifier's keys map contains only HS256. What does the safe verifier do?",
  "Rejects it before any cryptography runs",
  ["Tries HS256 with the same key as a fallback", "Verifies with EdDSA using the HS256 secret", "Accepts it if the claims are still valid"],
  "An algorithm that is not in the allow-list is rejected immediately. Falling back to another algorithm is exactly the confusion attack the rule prevents.",
  "Lesson 11 checkYourself")
Q(L, 39, 11, "debugging", 2, "PyJWT raised 'The specified alg value is not allowed', so a developer 'fixed' it like this. What is wrong?",
  "algorithms= is read from the token, so the attacker picks the algorithm",
  ["get_unverified_header contacts the issuer and is slow", "jwt.decode needs the private key, not the public key", "algorithms= must be a string, not a list"],
  "Pass a fixed list of the algorithms your issuer uses, never one read from the token. Reading the header itself is fine; letting it choose the algorithm is the bug.",
  "Lesson 11 troubleshooting",
  code='import jwt\n\ndef verify(token, key):\n    alg = jwt.get_unverified_header(token)["alg"]\n    return jwt.decode(token, key, algorithms=[alg], audience="orders-api")')
Q(L, 40, 11, "code-reading", 2, "The verifier allows 30 s of clock-skew leeway. What does this print?",
  "True False", ["True True", "False False", "False True"],
  "50 s past exp is beyond the 30 s leeway, so it is expired; 20 s past exp is inside the leeway. Keep leeway in seconds, not hours.",
  "Lesson 11 code (verify)",
  code="def expired(now, exp, leeway=30):\n    return now > exp + leeway\n\nprint(expired(1_000_050, 1_000_000), expired(1_000_020, 1_000_000))")
Q(L, 41, 11, "scenario", 2, "Tokens are rejected as 'not yet valid' right after they are issued. What should you do?",
  "Sync the clocks with NTP and keep the leeway at a few seconds",
  ["Raise the leeway to 12 hours", "Stop checking nbf and exp", "Switch the issuer to HS256"],
  "Clock skew between issuer and API causes this; fix the clocks and keep leeway small. A huge leeway lets stolen expired tokens keep working.",
  "Lesson 11 troubleshooting")
Q(L, 42, 11, "concept", 2, "In the key-confusion test, the naive verifier accepts a forged HS256 token. How does 'one key per algorithm' stop it?",
  "The EdDSA public key can never be used as an HMAC secret",
  ["HS256 tokens are always shorter than EdDSA ones", "The public key is kept secret, so an attacker cannot guess it", "The verifier hashes the token twice"],
  "The attack signs with HMAC using the public key bytes as the secret; binding each key to one algorithm makes HS256 unknown. Public keys are public, so hiding them is not a defence.",
  "Lesson 11 concepts / expectedResults")

# ------------------------------------------------------------------ L300
L = "L300"
Q(L, 1, 12, "calculation", 2, "wrap() stores nonce || AESGCM(KEK).encrypt(nonce, DEK, kid) for a 32-byte DEK and a 12-byte nonce. How many bytes is the wrapped DEK?",
  CALC, ["44 bytes", "48 bytes", "76 bytes"],
  "12-byte nonce + 32-byte encrypted DEK + 16-byte tag = 60 bytes; the kid is AAD, so it adds nothing. 44 forgets the tag.",
  "Lesson 12 concepts / code (wrap)")
Q(L, 2, 12, "calculation", 3, "A store holds 2,000,000 records of 1 MiB each, each with a 60-byte wrapped DEK. Roughly how much data does a rewrap move, compared with re-encrypting everything?",
  CALC, ["about 1.9 TiB vs about 114 MiB", "about 114 MiB vs about 114 MiB", "about 1.9 TiB vs about 1.9 TiB"],
  "Rewrap only touches the wrapped keys (2,000,000 x 60 B), while re-encryption reads and writes all data. That is why envelope rotation takes seconds, not hours.",
  "Lesson 12 concepts / tradeOffs")
Q(L, 3, 12, "concept", 2, "Why does rotate() add a new KEK version instead of replacing the key?",
  "Existing records name the old version in their header and still need it",
  ["Replacing keys in place is slower than adding", "AES-GCM keys can only be used once", "Old versions are needed to sign new records"],
  "Each record's header points to the KEK version that wrapped its DEK; replacing the key would make them undecryptable. Rotation adds a version and makes it primary.",
  "Lesson 12 concepts / checkYourself")
Q(L, 4, 12, "concept", 2, "What tells you it is safe to retire orders-kek:v1?",
  "records_by_kid shows zero records still wrapped by v1",
  ["v2 has been the primary version for at least 24 hours now", "The rewrap job was started successfully", "No new records were written with v1 today"],
  "Retire only when the per-version record count is zero. A started or recently run job can crash part-way, as the failure lab shows.",
  "Lesson 12 concepts / checkYourself")
Q(L, 5, 12, "concept", 3, "Why is the kid passed as AAD when wrapping a DEK?",
  "A header edited to another version fails authentication",
  ["It makes the wrapped DEK shorter", "It lets the KMS find the key without a lookup", "It encrypts the kid so attackers cannot read which version is used"],
  "AAD binds the label to the wrapped key, so relabelling gives InvalidTag instead of silently trying another key. AAD is authenticated, not encrypted.",
  "Lesson 12 concepts / checkYourself")
Q(L, 6, 12, "code-reading", 2, "A simplified rewrap job moves records from v2 to v3 and crashes. What does this print?",
  "[('v2', 5), ('v3', 1)]", ["[('v2', 6)]", "[('v3', 6)]", "[('v2', 4), ('v3', 2)]"],
  "The loop moves record 0, then breaks when i reaches crash_after=1, leaving one record on v3 and five on v2. Deleting v2 now would lose five records.",
  "Lesson 12 failureLab",
  code='from collections import Counter\nrecords = ["v2"] * 6\ncrash_after = 1\nfor i in range(len(records)):\n    if i == crash_after:\n        break\n    records[i] = "v3"\nprint(sorted(Counter(records).items()))')
Q(L, 7, 12, "debugging", 3, "After a crashed rewrap job, an operator calls this retire(). Five orders become unreadable. What is the fix?",
  "Check the per-version record count and raise KeyInUse if it is not zero",
  ["Catch UnknownKey on read and fall back to the current primary KEK instead", "Re-encrypt the data with v3 before deleting v2", "Rotate again so a fresh version replaces v2"],
  "Retirement must ask the data first: count records per kid and refuse while any remain, then resume the rewrap. Falling back to another KEK cannot decrypt a DEK wrapped by v2.",
  "Lesson 12 failureLab",
  code='def retire(ring, version: int) -> None:\n    if version == ring.primary:\n        raise ValueError("cannot retire the primary")\n    del ring.versions[version]')
Q(L, 8, 12, "design", 3, "Several production services share keys for encrypting customer records and need an audit trail. Which option fits?",
  "Encryption as a service (OpenBao transit or a cloud KMS)",
  ["A KEK file copied into each service's container image", "Re-encrypting all data under one shared key each month", "One environment variable holding the KEK in every service"],
  "A KMS keeps the KEK inside the service, offers rotate/rewrap and an audit log, at the cost of a network call. Copying the KEK into images spreads it everywhere.",
  "Lesson 12 tradeOffs / caution")
Q(L, 9, 12, "scenario", 3, "An incident report says some DEKs themselves may have been copied. What does rotation need now?",
  "Re-encrypt the data under new DEKs; rewrapping is not enough",
  ["Rewrap all DEKs under a new KEK version", "Delete the KEK version that wrapped them", "Rotate the KEK and raise min_decryption_version above the old one"],
  "Rewrapping protects the DEKs with a new KEK but leaves the same DEKs, which the attacker already has. The trade-off table names this as the case for full re-encryption.",
  "Lesson 12 tradeOffs")

Q(L, 10, 13, "calculation", 2, "The renewal loop schedules renewal at a jittered point between 60 % and 72 % of a 160-hour lifetime. Between which hours does renewal start?",
  CALC, ["hour 106.7 to hour 152", "hour 60 to hour 72", "hour 144 to hour 152"],
  "0.60 x 160 = 96 and 0.72 x 160 = 115.2, leaving many hours for retries. 60 to 72 confuses percentages with hours.",
  "Lesson 13 failureLab (fix)")
Q(L, 11, 13, "calculation", 2, "A static server's 160-hour certificate is checked every hour from hour 0 to hour 191. Handshakes fail from hour 160 on. How many hours fail?",
  CALC, ["31 hours", "33 hours", "160 hours"],
  "Hours 160 through 191 inclusive are 32 hours, matching the lab's '32 failed hours of 192'. 31 is the usual off-by-one.",
  "Lesson 13 expectedResults")
Q(L, 12, 13, "calculation", 2, "The alert fires when time-to-expiry drops below 25 % of the lifetime. For a 160-hour certificate, when does it fire?",
  CALC, ["120 hours left", "25 hours left", "16 hours left"],
  "25 % of 160 hours is 40 hours of remaining life, long before expiry. 120 hours is 75 % of the lifetime, which is when 25 % has been used.",
  "Lesson 13 failureLab (fix)")
Q(L, 13, 13, "concept", 2, "Why does the renewal schedule add jitter?",
  "Without it the whole fleet renews at once and overloads the CA",
  ["Jitter makes renewal times unpredictable, so certificates are harder to forge", "Jitter keeps the private key from being reused", "Jitter is required for the CA to sign a certificate"],
  "Many servers with the same fixed schedule hit the CA together and get rate-limited. Jitter is about load, not about forgery or key reuse.",
  "Lesson 13 checkYourself / tradeOffs")
Q(L, 14, 13, "concept", 2, "Why renew at about 60-72 % of the lifetime instead of at 95 %?",
  "To leave time for retries if the CA or network is down",
  ["Certificates become cryptographically weaker after half their lifetime", "CAs refuse renewals in the last 5 % of a lifetime", "Clients reject certificates in their final 30 %"],
  "Early renewal turns a CA outage into retries instead of an expiry outage; in the lab the CA is down for hours 90-124. Certificates do not weaken with age.",
  "Lesson 13 checkYourself")
Q(L, 15, 13, "scenario", 3, "A CRL verifies with the CA key, but its nextUpdate time has passed. What should a client do?",
  "Treat it as stale, fetch a new one, and apply a pre-decided policy",
  ["Trust it, because the signature is valid", "Ignore revocation and accept every certificate", "Treat every certificate on it as expired"],
  "A CRL is only as good as its signature and freshness; a stale list may miss new revocations. Decide in advance whether stale means fail closed or alert.",
  "Lesson 13 concepts / checkYourself")
Q(L, 16, 13, "debugging", 2, "The renewal job wrote a new certificate to disk, but clients still receive the old one. What is wrong?",
  "The server process never reloaded the certificate",
  ["The CA signed the new cert with the old key", "Clients cache certificates for the whole lifetime", "The new cert needs a longer lifetime than the old"],
  "Writing the file does not change a running process; hot-swap the certificate or restart after writing. TLS clients do not cache server certificates between handshakes.",
  "Lesson 13 troubleshooting",
  code='ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\nctx.load_cert_chain("server.pem", "server-key.pem")  # once, at start-up\nwhile True:\n    renew_if_due("server.pem", "server-key.pem")    # writes new files\n    serve_one_hour(ctx)')
Q(L, 17, 13, "code-reading", 2, "A client clock is 5 minutes behind the CA. What does this print?",
  "False True", ["True True", "False False", "True False"],
  "With notBefore at issue time, the client's 'now' is 5 minutes earlier, so the cert is not yet valid; backdating notBefore by 1 hour fixes it.",
  "Lesson 13 expectedResults",
  code='from datetime import datetime, timedelta\nissued = datetime(2026, 10, 29, 12, 0)\nclient_now = issued - timedelta(minutes=5)\nresults = []\nfor backdate in (timedelta(0), timedelta(hours=1)):\n    results.append(client_now >= issued - backdate)\nprint(*results)')
Q(L, 18, 13, "design", 3, "Field devices go online only a few times a year and cannot renew often. Which approach does the lesson's trade-off table suggest?",
  "Longer-lived certificates plus distributed CRLs",
  ["One-hour certificates renewed through ACME", "Certificates that never expire and no revocation", "Jittered renewal every 60 % of a 7-day lifetime"],
  "Short-lived certs need reliable renewal, which these devices cannot do, so longer lifetimes with CRLs fit. Certificates that never expire leave a leaked key valid forever.",
  "Lesson 13 tradeOffs")

Q(L, 19, 14, "concept", 2, "The manifest signature is valid. Why can the installed release still be malicious?",
  "Files outside the manifest or with changed digests are not covered unless checked",
  ["Ed25519 signatures can be replayed on another release", "The manifest covers names only, never the content", "Signatures stop being valid after the files are copied"],
  "The signature covers the digests, so the installer must verify every file and reject extra or missing ones. In the lab a swapped README and an extra .pth slip through.",
  "Lesson 14 concepts / checkYourself")
Q(L, 20, 14, "concept", 2, "Why must the installer verify the raw manifest bytes before calling json.loads?",
  "Re-serializing can change bytes and break or bypass verification",
  ["json.loads is slower than signature verification", "Parsed JSON cannot contain SHA-256 digests", "Signatures only work over UTF-16 text"],
  "Verify the exact bytes that were signed, then parse; key order and whitespace may change when you re-serialize. Speed is not the reason.",
  "Lesson 14 concepts / checkYourself")
Q(L, 21, 14, "debugging", 3, "This installer checks every file listed in a verified manifest, yet the tampered release installs 5 files. What is the bug?",
  "It copies every file in dist, including ones not in the manifest",
  ["It should compare the digests with == instead of != before copying", "It must verify the signature after copying", "rglob skips files in subfolders such as app/"],
  "Strict install allow-lists the manifest: unknown or missing files are rejected before copying. Here the extra app/zz_extra.pth is copied without any check.",
  "Lesson 14 failureLab",
  code='def install(dist, manifest, dest):\n    for name, digest in manifest["files"].items():\n        if sha256_file(dist / name) != digest:\n            raise ValueError(f"digest mismatch: {name}")\n    for path in dist.rglob("*"):\n        if path.is_file():\n            copy(path, dest / path.relative_to(dist))')
Q(L, 22, 14, "code-reading", 2, "What does this print?",
  "['app/zz_extra.pth'] []", ["['app/zz_extra.pth'] ['README.txt']", "[] []", "['README.txt'] []"],
  "on_disk minus signed gives the unknown file; signed minus on_disk is empty, so nothing is missing. A swapped README is still in both sets and needs a digest check to catch.",
  "Lesson 14 failureLab",
  code='signed = {"app/__init__.py", "app/core.py", "README.txt", "LICENSE"}\non_disk = signed | {"app/zz_extra.pth"}\nprint(sorted(on_disk - signed), sorted(signed - on_disk))')
Q(L, 23, 14, "scenario", 3, "You must rotate the release signing key without breaking existing installers. What order works?",
  "Ship the new kid to installers, sign with the new key, then remove the old kid",
  ["Sign with the new key now, then update installers when users report errors", "Remove the old kid first so no one can use the old key", "Sign every release with both keys forever"],
  "Installers must trust the new key before it is used, and the old key is removed after an overlap window. Removing it first breaks every installer that has not updated yet.",
  "Lesson 14 checkYourself")
Q(L, 24, 14, "design", 2, "A release has 40 artifacts. Which signing approach does the trade-off table favour?",
  "One signed manifest of digests, with the installer checking every file",
  ["One signature per artifact, without checking which files are in the set", "A plain SHA256SUMS file without a signature", "Signing only the largest artifact"],
  "One signature over all digests is cheap to verify for many files, as long as the installer checks each file and the file set. Per-artifact signatures miss unsigned extra files.",
  "Lesson 14 tradeOffs")
Q(L, 25, 14, "concept", 3, "A CI pipeline uses keyless signing with a transparency log (Sigstore). What must the verifier check besides 'it is signed'?",
  "The signer identity and the OIDC issuer it expects",
  ["That the signature is shorter than 64 bytes and uses Ed25519", "That the transparency log is offline", "That the private key file is still in CI"],
  "Anyone can get a keyless signature, so verify who signed and which issuer vouched for them. There is no long-lived private key to look for.",
  "Lesson 14 tradeOffs")
Q(L, 26, 14, "debugging", 2, "Why does this verification fail on a genuine release?",
  "It verifies re-serialized JSON, not the exact signed bytes",
  ["json.loads cannot read a manifest written as bytes", "Ed25519 needs the digest of the manifest, not the manifest", "The public key must sign the manifest again first"],
  "json.dumps(indent=2) produces different bytes from the signed file, so verification fails; verify raw then parse. Pretty-printing breaks the signature.",
  "Lesson 14 troubleshooting",
  code='import json\nfrom pathlib import Path\nraw = Path("manifest.json").read_bytes()\nmanifest = json.loads(raw)\npub.verify(sig, json.dumps(manifest, indent=2).encode())')
Q(L, 27, 14, "calculation", 2, "A release has 40 artifacts. How many signature bytes does Ed25519 signing produce per release with one signature per artifact vs one signed manifest?",
  CALC, ["64 B vs 2,560 B", "2,560 B vs 2,560 B", "1,280 B vs 64 B"],
  "40 x 64-byte Ed25519 signatures = 2,560 B, against a single 64-byte signature over the manifest. 1,280 B assumes 32-byte signatures, which is the key size.",
  "Lesson 14 tradeOffs")
Q(L, 28, 14, "concept", 2, "What does a valid signature on a release tell you?",
  "Who published it, not that its contents are safe",
  ["That the code was reviewed for malware before it was signed", "That it was built from the tagged source", "That all its dependencies are signed too"],
  "A signature proves origin and integrity since signing. It says nothing about whether the publisher's build or dependencies were safe.",
  "Lesson 14 caution")

Q(L, 29, 15, "concept", 2, "pyca/cryptography already passes Wycheproof. Why run Wycheproof vectors against your own code?",
  "Your wrapper adds parsing and size handling where bugs live",
  ["The library might be replaced by a different one at runtime", "Wycheproof vectors expire and must be re-run monthly", "Running vectors speeds up the library through caching"],
  "The derived vectors found truncated-tag and trailing-byte bugs in the wrappers, not in the library. Test your wrapper, not only the library.",
  "Lesson 15 concepts / checkYourself")
Q(L, 30, 15, "calculation", 2, "A lenient wrapper accepts a 4-byte truncated GCM tag. What is the chance that one random forgery attempt is accepted?",
  CALC, ["1 in 2^128", "1 in 2^16", "1 in 2^4"],
  "A 4-byte tag has 32 bits, so a guess succeeds with probability 2^-32, against 2^-128 for the full 16-byte tag. 2^4 confuses bytes with bits.",
  "Lesson 15 failureLab")
Q(L, 31, 15, "debugging", 3, "Derived vectors 9001/9002 (TruncatedTag) pass through this wrapper as valid. What is the fix?",
  "Require exactly 16-byte tags (or use the high-level AESGCM API)",
  ["Set min_tag_length=4 so tiny tags are refused", "Check the tag after calling update() rather than before decrypting", "Pad short tags with zero bytes to 16"],
  "Letting min_tag_length follow the input accepts any tag length the library allows. Exact sizes reject everything else; min_tag_length=4 still allows truncated tags.",
  "Lesson 15 failureLab",
  code="from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes\n\ndef open_(key, iv, ct, tag):\n    mode = modes.GCM(iv, tag, min_tag_length=len(tag))\n    d = Cipher(algorithms.AES(key), mode).decryptor()\n    return d.update(ct) + d.finalize()")
Q(L, 32, 15, "debugging", 3, "Derived vector 9101 (TrailingBytes) passes through this wrapper. What is the bug?",
  "It ignores extra bytes after the first 64 instead of rejecting them",
  ["Ed25519 signatures are 32 bytes long, so the 64-byte slice is too long", "verify() needs the message first and the signature second", "It should hash the message before verifying"],
  "Exact sizes and canonical encodings: a 65-byte signature must be rejected, not trimmed. The slice hides malleable input that other verifiers would refuse.",
  "Lesson 15 failureLab",
  code="def verify(pub, sig: bytes, msg: bytes) -> bool:\n    try:\n        pub.verify(sig[:64], msg)\n        return True\n    except Exception:\n        return False")
Q(L, 33, 15, "code-reading", 2, "What does this print?",
  "rejected", ["accepted", "ValueError", "accepted (65-byte signature trimmed)"],
  "The library refuses a signature with a trailing byte; only a wrapper that trims input would accept it. That is why the strict wrapper passes the bytes through unchanged.",
  "Lesson 15 concepts",
  code='from cryptography.exceptions import InvalidSignature\nfrom cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey\nk = Ed25519PrivateKey.generate()\nsig = k.sign(b"m")\ntry:\n    k.public_key().verify(sig + b"\\x00", b"m")\n    print("accepted")\nexcept InvalidSignature:\n    print("rejected")')
Q(L, 34, 15, "concept", 3, "Why do the lab's timing tests use medians over many interleaved rounds?",
  "Scheduler spikes and CPU frequency changes would otherwise dominate",
  ["Medians make the comparison constant-time", "Interleaving hides the secret from the measurement", "Averages are not allowed in security tests"],
  "Timing evidence is statistical: medians resist outliers and interleaving spreads noise across both guesses. None of this makes code constant-time.",
  "Lesson 15 checkYourself")
Q(L, 35, 15, "concept", 3, "A service checks for repeated nonces in memory while it runs. Why can it still miss nonce reuse?",
  "A restart clears its memory while a seeded PRNG repeats the same nonces",
  ["In-memory sets cannot hold 12-byte values", "Nonce reuse only happens across different keys", "The check runs after encryption, too late to log"],
  "Only an offline scan of stored ciphertexts sees nonces from both runs. In-process memory starts empty after each restart.",
  "Lesson 15 checkYourself")
Q(L, 36, 15, "design", 3, "Should a timing test in CI be your proof that a MAC comparison is safe?",
  "No: use it for gross leaks only; rely on compare_digest and review",
  ["Yes, once the ratio stays near 1.0 for a week", "Yes, if the test runs on a dedicated CI machine", "No: timing leaks cannot exist in Python code"],
  "Noise makes timing tests flaky and a missing signal proves nothing, so they catch only large effects. Python code can leak timing, as the early-exit compare shows.",
  "Lesson 15 tradeOffs / caution")
Q(L, 37, 15, "scenario", 2, "The timing test for the naive early-exit compare shows a ratio of about 1. What should you conclude?",
  "Nothing yet: raise repetitions or rounds; a small ratio is not proof of safety",
  ["The naive compare is constant-time on this machine", "The test is broken and should be deleted", "Python's == is constant-time for bytes"],
  "Too few repetitions or a noisy machine hide the effect. Never treat a small ratio as proof that the code is safe.",
  "Lesson 15 troubleshooting")

Q(L, 38, 16, "concept", 2, "Why does the lesson prefer a mounted secret file (NAME_FILE) over an environment variable?",
  "Env vars are inherited by child processes and appear in dumps and debug pages",
  ["Files are encrypted by the operating system automatically", "Environment variables cannot hold 40-character values", "Reading a file is faster than reading the environment"],
  "Environment variables spread to children, crash dumps and debug endpoints; OWASP advises against them unless nothing else works. Files are not encrypted automatically and need correct permissions.",
  "Lesson 16 concepts / tradeOffs")
Q(L, 39, 16, "concept", 2, "Why is the redaction filter attached to the log handler rather than to the logger?",
  "Logger filters skip records from child loggers; the handler sees all of them",
  ["Handlers run before loggers, so redaction happens earlier", "Logger filters cannot change the message text", "Handlers are created once per request"],
  "Records from child loggers propagate to parent handlers without passing the parent logger's filters. Putting the filter on the handler covers every record written.",
  "Lesson 16 checkYourself / troubleshooting")
Q(L, 40, 16, "code-reading", 3, "What does this print?",
  "leaked", ["clean", "AttributeError", "nothing"],
  "The filter is on the 'app' logger, but the record is logged on 'app.http' and propagates to app's handler without passing app's logger filters. Moving the filter to the handler gives 'clean'.",
  "Lesson 16 troubleshooting",
  code='import io, logging\nbuf = io.StringIO()\napp = logging.getLogger("app")\napp.addHandler(logging.StreamHandler(buf))\napp.propagate = False\napp.addFilter(lambda r: "sk_demo" not in r.getMessage())\nlogging.getLogger("app.http").warning("auth sk_demo_123")\nprint("leaked" if "sk_demo" in buf.getvalue() else "clean")')
Q(L, 41, 16, "scenario", 3, "An API key is rotated with a dual-validity window. When can you stop accepting the previous key?",
  "When logs show no successful auth with it for a while and the window has passed",
  ["As soon as the new key is deployed to all services", "Exactly 24 hours after rotation, whatever the logs say", "When the new key has been used at least once"],
  "Measure use of the old key before removing it; a deploy can miss a client. A fixed timer without evidence can lock out callers still on the old key.",
  "Lesson 16 concepts / checkYourself")
Q(L, 42, 16, "design", 2, "At start-up the service finds neither ORDERS_API_KEY_FILE nor ORDERS_API_KEY. What should it do?",
  "Fail closed: stop with a clear 'secret not configured' error",
  ["Continue with an empty key and log a warning for the operators", "Fall back to a default demo key in the code", "Generate a random key and keep running"],
  "Failing closed avoids running half-configured or with a known key. A default or random key either weakens security or breaks callers silently.",
  "Lesson 16 concepts / troubleshooting")
Q(L, 43, 16, "concept", 2, "In the lab an agent reviews logs for leaks. Why does code, not the agent, decide what is a leak?",
  "The agent's answers vary and can be wrong; the scanner is reproducible and tested",
  ["Agents cannot read JSON logs", "The scanner is faster than any model", "Agents may only see encrypted logs"],
  "In the lab the agent gave one false positive and two misses; the deterministic scanner gives the same tested result every run.",
  "Lesson 16 concepts / checkYourself")
Q(L, 44, 16, "design", 3, "A containerised service runs on Kubernetes. Which secret delivery does the lesson's trade-off table suggest, and with what caveat?",
  "A mounted secret file; Secrets are unencrypted in etcd by default",
  ["An environment variable, since it is the most portable option", "A secret baked into the image; it never changes", "A command-line flag; it is visible only to root"],
  "Mounted files are not inherited like env vars and Kubernetes updates them, but etcd encryption must be enabled. Baked-in secrets end up in every image copy.",
  "Lesson 16 tradeOffs")
Q(L, 45, 16, "code-reading", 2, "What does this print?",
  "Secret('***') 40", ["kkkkkkkkkk... 40", "Secret('***') 3", "<__main__.Secret object> 40"],
  "f-strings call __str__, which falls back to __repr__, so the value is masked; reveal() still returns the 40-character secret. The wrapper reduces accidental exposure but is not encryption.",
  "Lesson 16 expectedResults",
  code='class Secret:\n    def __init__(self, v):\n        self._v = v\n    def __repr__(self):\n        return "Secret(\'***\')"\n    def reveal(self):\n        return self._v\n\ns = Secret("k" * 40)\nprint(f"{s} {len(s.reveal())}")')
Q(L, 46, 16, "debugging", 3, "This redaction filter sits on the handler, but the scanner still finds the key in log.info('headers %s', headers). Why?",
  "It only checks record.msg; the key is in record.args",
  ["Handler filters run only after the record is already written", "logging.Filter cannot return a bool", "Filters cannot see INFO records"],
  "With %-style logging the template is in msg and values are in args; redact getMessage() or the args (including nested dicts). The filter placement is already correct.",
  "Lesson 16 troubleshooting",
  code='import logging\n\nclass Redact(logging.Filter):\n    def filter(self, record):\n        if "Bearer" in str(record.msg):\n            record.msg = "[REDACTED]"\n        return True')

# ------------------------------------------------------------------ L400
L = "L400"
Q(L, 1, 17, "calculation", 3, "A v2 envelope carries an Ed25519 signature and an ML-DSA-65 signature. How many signature bytes is that per envelope?",
  CALC, ["3,309 B", "128 B", "4,691 B"],
  "Ed25519 gives 64 B and ML-DSA-65 gives 3,309 B, so dual signing adds 3,373 B. 3,309 B counts the post-quantum signature only.",
  "Lesson 17 options / scalingLimits")
Q(L, 2, 17, "calculation", 3, "A format has 2 AEADs and 2 signature algorithms; the signature phase can be Ed25519, ML-DSA-65 or both. After adding a third AEAD, how many ids does each design need?",
  CALC, ["6 suite ids vs 4 algorithm ids", "9 suite ids vs 9 algorithm ids", "12 suite ids vs 5 algorithm ids"],
  "Suite ids multiply (3 AEADs x 3 signature phases = 9) while per-algorithm ids add (3 + 2 = 5). That combinatorial growth is why suites were rejected for this format.",
  "Lesson 17 options (C)")
Q(L, 3, 17, "concept", 3, "In the v2 envelope, what is the job of the 'aead' label in the header?",
  "It names the algorithm; the verifier's policy decides if it is acceptable",
  ["It tells the reader which algorithm it must accept", "It is a hint the reader can ignore and guess instead", "It encrypts the header under the chosen algorithm"],
  "Labels let readers dispatch without guessing, but a message's own field must never decide what is allowed. Policy is the gate.",
  "Lesson 17 concepts / caution")
Q(L, 4, 17, "concept", 3, "Client and server share no active algorithm during negotiation. What should happen?",
  "Fail with an error; never fall back to something outside policy",
  ["Fall back to the oldest algorithm that both sides still support today", "Pick the client's first choice anyway", "Send the data unencrypted with a warning"],
  "Negotiation fails closed: no common active algorithm means an error. Fallbacks are what downgrade attacks exploit.",
  "Lesson 17 concepts")
Q(L, 5, 17, "scenario", 3, "A256GCM is deprecated and C20P1305 is the new default. When may A256GCM move to disallowed?",
  "When envelopes_by_aead shows 0 records still using it",
  ["Immediately, since the default has already changed to C20P1305", "After a fixed 90 days, whatever the metric says", "When no new A256GCM records were sealed this week"],
  "Disallowing an algorithm makes every record that still uses it unreadable, so wait for the per-algorithm count to reach zero. Changing the default does not migrate old data.",
  "Lesson 17 checkYourself")
Q(L, 6, 17, "debugging", 3, "A forged envelope with only an Ed25519 signature passes this verifier. What is the bug?",
  "It checks whatever signatures the envelope lists instead of the ones policy requires",
  ["It should verify ML-DSA-65 before Ed25519", "It must catch InvalidSignature and return False", "It should verify the payload hash, not the payload"],
  "The envelope is attacker-controlled, so removing the ML-DSA entry removes that check (signature stripping). The verifier must require the policy's signatures and fail if one is missing.",
  "Lesson 17 failureLab",
  code='def verify(env: dict, data: bytes, keys: dict) -> bool:\n    for alg, sig in env["sigs"]:\n        keys[alg].verify(sig, data)  # raises if invalid\n    return True')
Q(L, 7, 17, "design", 3, "Why is each data key bound to exactly one algorithm id in the registry?",
  "A relabelled header cannot reuse the key under another algorithm",
  ["It lets one key serve every algorithm, which saves key storage space", "It is needed for the header to fit in 74 bytes", "It allows the reader to try algorithms until one works"],
  "Using one key across algorithms invites cross-algorithm attacks; open_ refuses a header whose label disagrees with the key's binding. Trial decryption is what the design avoids.",
  "Lesson 17 checkYourself / troubleshooting")
Q(L, 8, 17, "calculation", 3, "Millions of 200-byte records are each dual-signed (3,373 B of signatures, computed from the real sizes). What is the ratio of signature bytes to payload bytes?",
  CALC, ["about 168.6x", "about 1.0x", "about 3.4x"],
  "3,373 / 200 is about 16.9, far above the scaling signal of 1. The lesson's answer is to sign batches or manifests instead of each record.",
  "Lesson 17 scalingLimits")

Q(L, 9, 18, "calculation", 3, "In X25519MLKEM768, the client share is the ML-KEM-768 encapsulation key plus an X25519 public key; the server share is the ML-KEM ciphertext plus an X25519 public key. What sizes result?",
  CALC, ["client 1,184 B, server 1,088 B", "client 1,120 B, server 1,216 B", "client 2,336 B, server 2,336 B"],
  "1,184 + 32 = 1,216 B and 1,088 + 32 = 1,120 B, 2,336 B on the wire. Forgetting the 32-byte X25519 part gives the pure ML-KEM sizes.",
  "Lesson 18 expectedResults")
Q(L, 10, 18, "calculation", 3, "Roughly how many times larger is an ML-DSA-65 signature than an Ed25519 signature?",
  CALC, ["about 2x", "about 10x", "about 200x"],
  "3,309 B / 64 B is about 52x, which is why PQ signatures cost far more bytes than PQ key exchange. Key-exchange shares grow much less.",
  "Lesson 18 concepts")
Q(L, 11, 18, "concept", 3, "Why does key exchange migrate to post-quantum before signatures?",
  "Recorded exchanges can be decrypted later; signatures only need to hold while verified",
  ["PQ signatures are not yet standardised", "Key exchange is cheaper to change in every protocol", "Signatures are already quantum-safe"],
  "Harvest now, decrypt later threatens today's recorded traffic, while a forged signature needs a quantum computer at verification time. ML-DSA is standardised; that is not the reason.",
  "Lesson 18 concepts / checkYourself")
Q(L, 12, 18, "concept", 3, "Why does the hybrid combine the two shared secrets by concatenation and a KDF over the transcript, rather than XOR?",
  "It stays secure if either secret is strong and binds the key to the exact shares",
  ["XOR is too slow for 64-byte secrets", "Concatenation makes the key twice as long, so it is twice as strong against attacks", "XOR would reveal both secrets to an eavesdropper"],
  "Concatenate-then-KDF with the shares is the RFC 10024 construction and keeps security if either part holds. Key length alone is not the point.",
  "Lesson 18 checkYourself")
Q(L, 13, 18, "scenario", 3, "The client expects a 1,120-byte server share but receives 32 bytes. What does a correct client do?",
  "Abort with illegal_parameter and log it",
  ["Use the 32 bytes as an X25519-only exchange", "Pad the share to 1,120 bytes and continue", "Retry the handshake without ML-KEM"],
  "A short share is a downgrade attempt; deriving a classical-only key lets a future quantum attacker recover it. Retrying without ML-KEM is the same downgrade by another route.",
  "Lesson 18 failureLab / checkYourself")
Q(L, 14, 18, "code-reading", 3, "What does this print?",
  "abort: illegal_parameter | ok", ["ok | ok", "ok | abort: illegal_parameter", "abort: illegal_parameter | abort: illegal_parameter"],
  "A 32-byte share is not the expected 1,088 + 32 = 1,120 bytes, so it aborts; a 1,120-byte share passes. Exact length checks are what stop the downgrade.",
  "Lesson 18 failureLab (fix)",
  code='EXPECTED = 1088 + 32\n\ndef check_share(share: bytes) -> str:\n    if len(share) != EXPECTED:\n        return "abort: illegal_parameter"\n    return "ok"\n\nprint(check_share(bytes(32)), "|", check_share(bytes(1120)))')
Q(L, 15, 18, "design", 3, "Traffic must stay confidential for 10 years and ML-KEM is still young. Which key exchange does ADR-0018 choose?",
  "Hybrid X25519MLKEM768 with strict share checks",
  ["X25519 only, because it is fastest", "ML-KEM-768 only, because it is already post-quantum", "X25519 now, switching to ML-KEM in 10 years"],
  "Hybrid stays secure if either component holds, covering both a quantum attacker and an early lattice break. ML-KEM alone has no safety net, and X25519 alone fails the 10-year constraint.",
  "Lesson 18 options / tradeOffs")
Q(L, 16, 18, "design", 3, "ML-DSA certificate chains are about 30x larger than classical ones. What does the lesson advise for certificates today?",
  "Keep classical certificates until signature migration is planned",
  ["Switch every chain to ML-DSA now, together with the key exchange move", "Drop certificates and rely on the hybrid KEM", "Use ML-KEM keys inside certificates instead"],
  "Signature migration is less urgent and costs handshake bytes and latency, so watch those signals first. A KEM does not authenticate the server.",
  "Lesson 18 scalingLimits")

Q(L, 17, 19, "concept", 3, "With a PKCS#11 token, what does the application hold?",
  "A handle that asks the token to use the key",
  ["An encrypted copy of the private key", "The private key, unlocked by the PIN", "A certificate that contains the encrypted private key"],
  "The key stays inside the token and the app sends sign requests by handle. The PIN unlocks the session, not the key bytes.",
  "Lesson 19 concepts")
Q(L, 18, 19, "concept", 3, "An attacker controls the build host that uses a non-exportable token key. What does non-exportability still give you?",
  "No signing after clean-up, and audit events for what they signed",
  ["The attacker cannot sign anything at all while they are on the host", "The token wipes itself when the host is compromised", "Signatures made by the attacker are marked invalid"],
  "While in, the attacker can ask the token to sign; non-exportability turns theft into bounded, logged misuse. It does not stop signing during the compromise.",
  "Lesson 19 concepts / checkYourself")
Q(L, 19, 19, "concept", 3, "Why must the token, not the application, decide CKA_EXTRACTABLE?",
  "Defaults vary by token and an application template can be wrong or compromised",
  ["Applications cannot set attributes in PKCS#11", "The token runs faster when it chooses attributes", "Extractable keys cannot sign data"],
  "In the failure lab the app trusted token defaults (extractable) and the key was read out. Token policy is the boundary because it does not depend on application code.",
  "Lesson 19 checkYourself / failureLab")
Q(L, 20, 19, "concept", 3, "What does CKA_NEVER_EXTRACTABLE=True prove that CKA_EXTRACTABLE=False does not?",
  "The key was never extractable at any point in its life",
  ["The key cannot be used for signing", "The key was imported from a backup", "The key can still be copied to another token by the security officer"],
  "EXTRACTABLE=False describes now; NEVER_EXTRACTABLE shows the key was not imported or switched later. An imported key can have EXTRACTABLE=False and still have existed outside.",
  "Lesson 19 checkYourself")
Q(L, 21, 19, "debugging", 3, "Generating a key on the hardened token fails with CKR_TEMPLATE_INCONSISTENT. What does it mean?",
  "The template asked for an extractable or non-sensitive private key",
  ["The user PIN was entered wrongly three times, so the token is locked", "The PKCS11_MODULE path is not set", "The token has run out of storage"],
  "The hardened token refuses opt-outs from SENSITIVE/non-EXTRACTABLE by design; fix the template. A wrong PIN gives CKR_PIN_INCORRECT and a missing module gives a KeyError.",
  "Lesson 19 troubleshooting",
  code='template = {"CKA_SENSITIVE": False, "CKA_EXTRACTABLE": True, "CKA_SIGN": True}\nkey = session.generate_keypair("Ed25519", private_template=template)\n# -> CKR_TEMPLATE_INCONSISTENT')
Q(L, 22, 19, "design", 3, "Twenty services must sign or decrypt, and key use must be centrally revocable. Which option fits?",
  "A KMS-style service (OpenBao transit or cloud KMS)",
  ["A PKCS#11 token on each of the twenty hosts", "A PEM key file per service, protected with a password", "One shared PEM key mounted into all services"],
  "Central policy, audit and instant disable fit many consumers; per-host tokens multiply ceremonies and PINs. A PEM file gives permanent signing power to whoever reads it.",
  "Lesson 19 tradeOffs / scalingLimits")
Q(L, 23, 19, "calculation", 3, "Signing takes about 40.1 µs via the token and about 5001.5 µs via the KMS over HTTP. Signing one at a time, how many signatures per second is each?",
  CALC, ["about 40 vs about 5,002", "about 2,494 vs about 20", "about 24,938 vs about 2,000"],
  "1,000,000 µs / 40.1 µs is about 24,938 and 1,000,000 / 5001.5 is about 200. The KMS misses a 1 ms budget without connection reuse.",
  "Lesson 19 options")
Q(L, 24, 19, "code-reading", 3, "An inventory fitness check scans token keys. What does this print?",
  "['legacy', 'imported']", ["['legacy']", "['imported']", "[]"],
  "A key passes only if it is ALWAYS_SENSITIVE and NEVER_EXTRACTABLE; the imported key fails because it was once extractable. Checking only EXTRACTABLE would miss it.",
  "Lesson 19 fitnessFunction",
  code='keys = [\n    {"label": "release", "ALWAYS_SENSITIVE": True, "NEVER_EXTRACTABLE": True},\n    {"label": "legacy", "ALWAYS_SENSITIVE": False, "NEVER_EXTRACTABLE": False},\n    {"label": "imported", "ALWAYS_SENSITIVE": True, "NEVER_EXTRACTABLE": False},\n]\nbad = [k["label"] for k in keys if not (k["ALWAYS_SENSITIVE"] and k["NEVER_EXTRACTABLE"])]\nprint(bad)')
Q(L, 25, 19, "scenario", 3, "A single HSM holds the production release key, generated non-exportable. What does the lesson warn about?",
  "It cannot be restored from software backups; provision a second device in the ceremony",
  ["It must be exported once a year for safekeeping", "Its key should be copied to a PEM file as a backup", "It needs a longer PIN to survive hardware failure"],
  "Non-exportable keys cannot come back from a file backup, so plan a second device and rehearse rotation. Exporting it defeats the point of the token.",
  "Lesson 19 scalingLimits")

Q(L, 26, 20, "calculation", 3, "With sender keys, removing a member costs (n-1)(n-2) encryptions. How many for a group of n = 64?",
  CALC, ["63", "4,032", "10"],
  "63 x 62 = 3,906: every remaining member sends a new sender key to every other remaining member. 10 is the MLS-style tree cost at the same size.",
  "Lesson 20 options / checkYourself")
Q(L, 27, 20, "calculation", 3, "For a group of 256, how many encryptions does pairwise fan-out need per message, and how many HPKE encryptions does a full-tree MLS-style commit need?",
  CALC, ["1 and 8", "255 and 255", "256 and 16"],
  "Pairwise sends the message to each of the n - 1 = 255 others; a commit costs about log2(256) = 8 encryptions. MLS still needs only 1 encryption per application message.",
  "Lesson 20 concepts / options")
Q(L, 28, 20, "concept", 3, "Why can't a new epoch secret simply be HKDF(old epoch secret)?",
  "The removed member knows the old secret and could derive the new one",
  ["HKDF output is too short for an epoch secret", "HKDF cannot run on every member at once", "The new epoch must use a different hash function"],
  "Only fresh entropy delivered to the remaining members excludes someone who knew the old secret. HKDF is deterministic, so it gives the removed member the same result.",
  "Lesson 20 concepts / checkYourself")
Q(L, 29, 20, "concept", 3, "What is the difference between forward secrecy (FS) and post-compromise security (PCS)?",
  "FS protects past messages; PCS restores secrecy after the compromised member updates",
  ["FS protects future messages; PCS protects past messages", "FS needs a tree; PCS works only for pairwise chats", "They are two names for the same property"],
  "Forward secrecy means a compromise today does not reveal yesterday's messages; PCS heals the group once fresh keys replace the stolen ones. FS alone does not heal.",
  "Lesson 20 concepts / checkYourself")
Q(L, 30, 20, "debugging", 3, "After frank removes dave, dave can still read the next epoch. What is wrong with this _remove?",
  "It blanks dave's leaf but not the parents on his direct path",
  ["It should delete dave's stored messages from the delivery server", "It must re-encrypt all past epochs", "It should send dave a new path secret"],
  "Dave still knows the old secrets of his parent nodes; blank the leaf and its direct path (RFC 9420 12.1.3) so the commit uses fresh secrets he never sees.",
  "Lesson 20 failureLab",
  code="def _remove(self, leaf: int) -> None:\n    self.tree[leaf] = None  # blank the removed member's leaf\n    # parents of the leaf keep their old secrets\n    self.commit(fresh_path_from=self.me)")
Q(L, 31, 20, "code-reading", 3, "In an array-based tree with 8 leaves, leaf i is node i + 8 and a node's parent is node // 2. What does this print?",
  "[5, 2, 1]", ["[11, 5, 2]", "[5, 2]", "[1, 2, 5]"],
  "Leaf 3 is node 11; its parents are 5, 2 and the root 1, so three nodes (log2 8) must be blanked or re-keyed. The list starts at the parent, not the leaf itself.",
  "Lesson 20 concepts (direct path)",
  code="def direct_path(leaf: int, n_leaves: int) -> list:\n    node, path = leaf + n_leaves, []\n    while node > 1:\n        node //= 2\n        path.append(node)\n    return path\n\nprint(direct_path(3, 8))")
Q(L, 32, 20, "scenario", 3, "Members of one group end up in different epochs. What is the cause and fix?",
  "Commits were applied in different orders; the delivery service must order commits per group",
  ["Some members have slow clocks; sync NTP", "HPKE failed for one member; retry the commit", "The group grew too large; split it in two"],
  "Commits must be totally ordered per group, otherwise two committers in one epoch fork the state. Clock sync does not order commits.",
  "Lesson 20 troubleshooting / scalingLimits")
Q(L, 33, 20, "design", 3, "Some members never send updates. Which policy does the lesson recommend to keep post-compromise security?",
  "Require updates on a schedule and remove members who never update",
  ["Rely on forward secrecy, which already covers members who stay idle", "Rotate the group's root secret with HKDF each day", "Re-send old messages so idle members stay in sync"],
  "PCS only arrives when members update, so track leaf-key age and enforce updates (RFC 9420 3.2). A deterministic HKDF ratchet does not add fresh entropy.",
  "Lesson 20 scalingLimits")

Q(L, 34, 21, "concept", 3, "In the threat-model-as-code checker, when does a control count?",
  "Only when its test exists and passes",
  ["When its description is in model.json", "When a reviewer has approved its name", "When an agent confirms it exists"],
  "Descriptions survive refactors that delete the protection; a missing or failing test is detectable in CI. Names and approvals do not prove the control still works.",
  "Lesson 21 concepts / checkYourself")
Q(L, 35, 21, "concept", 3, "Which STRIDE threats must every boundary-crossing flow have in this model?",
  "Tampering and Information disclosure",
  ["Spoofing and Repudiation", "Denial of service and Elevation of privilege", "Repudiation and Information disclosure"],
  "Data that crosses a trust boundary can be changed or read by whoever controls the wire or the other side. Spoofing applies to the parties, not to the flow itself.",
  "Lesson 21 concepts / checkYourself")
Q(L, 36, 21, "concept", 3, "What does an attack tree add to STRIDE per element?",
  "Prioritisation: which control closes the cheapest path to a goal",
  ["A complete list of every possible threat to each element of the system", "Proof that every control has a test", "Automatic fixes for each threat"],
  "STRIDE gives coverage; the attack tree shows which control matters most for a concrete attacker goal. The checker, not the tree, proves controls have tests.",
  "Lesson 21 concepts / checkYourself")
Q(L, 37, 21, "code-reading", 3, "OR nodes take the cheapest child, AND nodes add their children, and closed leaves cost infinity. What does this print?",
  "9 8", ["9 9", "8 8", "8 9"],
  "With the control closed the AND path is infinite, so the cheapest path is 9; once its test is deleted the leaf reopens and 2 + 1 + 5 = 8 wins. The cost drops from 9 to 8, as in the lab.",
  "Lesson 21 failureLab / options (B)",
  code='def cost(n):\n    if "leaf" in n:\n        return float("inf") if n.get("closed") else n["leaf"]\n    kids = [cost(c) for c in n["kids"]]\n    return min(kids) if n["op"] == "OR" else sum(kids)\n\nguard = {"leaf": 1, "closed": True}\ntree = {"op": "OR", "kids": [{"leaf": 9},\n        {"op": "AND", "kids": [{"leaf": 2}, guard, {"leaf": 5}]}]}\nfirst = cost(tree)\nguard["closed"] = False  # the control\'s test was deleted\nprint(first, cost(tree))')
Q(L, 38, 21, "debugging", 3, "After a refactor deleted the test behind C-NO-FALLBACK, this checker still reports no problems. Why?",
  "It checks only that a test name is recorded, not that the test exists and passes",
  ["It should check the control ids in alphabetical order", "It must run before the refactor, not after", "Controls need two tests each to be counted"],
  "A name-only check misses drift; controls must point to existing (and in CI, passing) tests. The order of checks is irrelevant.",
  "Lesson 21 failureLab",
  code='def check(model: dict) -> list:\n    problems = []\n    for c in model["controls"]:\n        if not c.get("test"):\n            problems.append(f"{c[\'id\']}: no test named")\n    return problems')
Q(L, 39, 21, "design", 3, "How does ADR-0021 use agent brainstorming in threat modelling?",
  "As input to a human session; code classifies and nothing merges automatically",
  ["As the threat model of record, updated each sprint", "To decide which controls pass, replacing the checker", "To auto-merge new threats when confidence is high"],
  "Agents give breadth but invent elements and controls; in the lab 3 of 6 proposals were rejected. The checker decides and a human accepts.",
  "Lesson 21 options (C) / tradeOffs")
Q(L, 40, 21, "scenario", 3, "A control test fails in the fitness run. What should you do?",
  "Fix the code the control protects; keep the mapping",
  ["Remove the control mapping so the build passes", "Mark the test as skipped until next sprint", "Replace the failing test with a description of the control"],
  "A failing control test means the control is broken. Removing the mapping hides the gap that the threat model exists to show.",
  "Lesson 21 troubleshooting")

Q(L, 41, 22, "calculation", 3, "Milestone M4 shares a 32-byte DEK with HPKE using the MLKEM768_X25519 (X-Wing) KEM and AES-256-GCM. How large is the wrapped DEK?",
  CALC, ["1,120 bytes", "80 bytes", "1,216 bytes"],
  "HPKE output is the 1,120-byte encapsulated key plus 32 bytes of ciphertext and a 16-byte tag. 1,120 counts only the KEM part.",
  "Lesson 22 expectedResults (M4)")
Q(L, 42, 22, "concept", 3, "An attacker owns the doc-service host. Why can they still read documents, and what limits it?",
  "They can ask the KMS to unwrap while in; the KEK stays in the KMS and audit rules flag bursts",
  ["They cannot read anything, because documents are encrypted", "They can copy the KEK and read documents forever", "They can read only documents that were never rotated"],
  "Access while on the host is possible but bounded and visible: the KEK never leaves the KMS and unwrap bursts are flagged. Encryption at rest does not stop a host that can call the KMS.",
  "Lesson 22 checkYourself")
Q(L, 43, 22, "concept", 3, "The audit log is signed per entry and hash-chained. What does the hash chain detect that signatures alone do not?",
  "Deleted or reordered entries",
  ["Entries signed with the wrong key", "Entries with a changed message body", "Entries written by the agent"],
  "Each entry commits to the previous one, so removing or moving an entry breaks the chain and the sequence. A per-entry signature already catches a changed entry.",
  "Lesson 22 checkYourself")
Q(L, 44, 22, "concept", 3, "The agent's explanation lists an anomaly A99 that no rule reported. What happens to it?",
  "It is rejected: the agent explains, code decides what is an anomaly",
  ["It is added to the scorecard as a new finding for the next review", "It triggers a page to on-call for review", "It replaces the rule output for that entry"],
  "Audit rules decide and the agent only explains, so unknown anomaly ids are rejected. Letting the agent add findings would make verdicts non-reproducible.",
  "Lesson 22 checkYourself / concepts")
Q(L, 45, 22, "code-reading", 3, "An attacker deletes entry e2 from a hash-chained log but keeps the stored hashes of e1 and e3. What does this print?",
  "[True, False]", ["[True, True]", "[False, False]", "[False, True]"],
  "e1 still links to the genesis value, but e3's stored hash was computed over e2's hash, so recomputing from e1 gives a different value. That is the chain_break finding.",
  "Lesson 22 expectedResults (M3)",
  code='import hashlib\ndef link(prev, entry):\n    return hashlib.sha256(prev + entry).digest()\nentries, chain, h = [b"e1", b"e2", b"e3"], [], b"\\0" * 32\nfor e in entries:\n    h = link(h, e)\n    chain.append(h)\nkept = [(entries[0], chain[0]), (entries[2], chain[2])]\nh, ok = b"\\0" * 32, []\nfor e, stored in kept:\n    h = link(h, e)\n    ok.append(h == stored)\nprint(ok)')
Q(L, 46, 22, "debugging", 3, "Your own test client gets SSLEOFError when calling the capstone KMS. What is the likely cause?",
  "It did not load the client certificate and key from the capstone PKI",
  ["The KMS certificate expired during the test", "The KEK was retired while the client was still connected to the KMS", "The client used TLS 1.3 instead of TLS 1.2"],
  "The KMS requires mTLS and closes the connection when no valid client certificate is presented. Expiry would show a verify error, not an EOF.",
  "Lesson 22 troubleshooting",
  code='ctx = ssl.create_default_context(cafile="pki/ca.pem")\nwith socket.create_connection(("127.0.0.1", 9443)) as raw:\n    with ctx.wrap_socket(raw, server_hostname="kms.local") as tls:\n        tls.sendall(b\'{"op": "unwrap"}\')')
Q(L, 47, 22, "scenario", 3, "Retiring docs-kek:v1 raises PermissionError: KeyInUse ... still wraps 3 record(s). What should you do?",
  "Run svc.rewrap() to finish moving records, then retire again",
  ["Delete the 3 records so v1 can be retired", "Force retire; the records will switch over to v2 automatically", "Restore v1 from backup after retiring it"],
  "The refusal is the safety check working: finish the rewrap, see the count reach zero, then retire. Forcing it makes those records unreadable, as lesson 12 showed.",
  "Lesson 22 troubleshooting / expectedResults (M1)")
Q(L, 48, 22, "design", 3, "How does the KMS in the capstone know which service is calling?",
  "From the client certificate presented in mTLS",
  ["From a service name sent in the JSON request body", "From the caller's source IP address", "From an API key in an environment variable"],
  "Identity comes from the verified client certificate, so it cannot be claimed by editing a request. Body fields and IP addresses are easy to fake or change.",
  "Lesson 22 concepts")


def run_snippet(code):
    return qc.run_snippet(code)


def build():
    out = {}
    for level, items in BANK.items():
        nums = [q["num"] for q in items]
        assert nums == list(range(1, len(items) + 1)), f"{level}: numbering {nums}"
        rng = random.Random(f"cr-{level}")
        positions = [i % 4 for i in range(len(items))]
        rng.shuffle(positions)
        qs = []
        for q, pos in zip(items, positions):
            qid = f"cr-{level}-{q['num']:03d}"
            if q["type"] == "calculation":
                assert q["correct"] is CALC, f"{qid}: calculation must take its answer from code"
                correct = qc.CALC[qid]()
            else:
                assert q["correct"] is not CALC, qid
                correct = q["correct"]
            if q["type"] == "code-reading" and "What does this print?" in q["question"]:
                out_text = run_snippet(q["code"])
                assert out_text == correct, f"{qid}: snippet printed {out_text!r}, expected {correct!r}"
                correct = out_text
            assert len(q["wrong"]) == 3 and correct not in q["wrong"], qid
            options = list(q["wrong"])
            options.insert(pos, correct)
            rec = {"id": qid, "level": level, "lesson": q["lesson"], "type": q["type"], "difficulty": q["difficulty"],
                   "question": q["question"]}
            if q["code"]:
                assert len(q["code"].splitlines()) <= 15, f"{qid}: snippet too long"
                rec["code"] = q["code"]
            rec.update({"options": options, "answer": pos, "explanation": q["explanation"], "source": q["source"]})
            qs.append(rec)
        out[level] = qs
    folder = TOPIC / "content" / "qbank"
    folder.mkdir(exist_ok=True)
    for level, qs in out.items():
        p = folder / f"{level}.json"
        if p.exists():
            p.unlink()  # mount does not support in-place replace
        p.write_text(json.dumps(qs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        longest = sum(1 for q in qs if max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
        print(f"{level}: {len(qs)} questions, correct option longest in {longest}")


if __name__ == "__main__":
    build()
