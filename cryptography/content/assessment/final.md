# Final exam (week 14) - 150 minutes, 100 marks

**Covers:** the whole course, L100-L500 (lessons 1-27).
**Rules:** closed book. Two A4 sheets of your own notes are allowed. A calculator is allowed.
**Answers:** model answers and marking points are below. The numeric values were verified with the lab code (labs/L500) and with lab outputs quoted in the lessons.

---

## Q1 - Derivation (12 marks)
(a) Derive the lower bound Pr[collision] ≥ 1 − exp(−q(q−1)/(2N)) for q uniform samples from N values. State exactly where you use independence. (6)
(b) A fleet encrypts 50,000 messages per second under one key with random 96-bit nonces. How many days until it reaches 2^32 messages? (3)
(c) With 192-bit nonces (XChaCha20-Poly1305), bound the collision probability after 2^32 messages. (3)

**Model answer.**
(a) Pr[no collision] = ∏_{i<q}(1 − i/N). Independence enters in the conditional factor (1 − i/N) for the (i+1)-th draw. Applying 1 − x ≤ e^(−x) to each factor gives Pr[no collision] ≤ exp(−Σi/N) = exp(−q(q−1)/(2N)); take the complement. [6]
(b) 2^32 / (5·10^4 · 86,400) ≈ **0.99 days**: about one day per key. [3]
(c) q²/(2N) ≈ 2^64/2^193 = **2^−129**. [3]

## Q2 - Proof (12 marks)
Prove that the one-time pad is perfectly secret for every message distribution, and that any perfectly secret scheme needs |K| ≥ |M|. Then explain in two sentences why the course nonetheless uses AES-GCM.

**Model answer.**
- Proofs as in T25.1(a) and (b). [5 + 5]
- The OTP needs a key as long as all traffic, delivered securely and never reused, and it provides no integrity. AEAD gives computational IND-CCA security with 256-bit keys and built-in integrity (lesson 25, L100 #4). [2]

## Q3 - Prediction (10 marks)
In the L300 envelope-encryption design, data keys are wrapped under versioned KEKs and the KEK is rotated. Predict which of the following still decrypt after rotation, and explain why: (a) documents sealed before the rotation, while the old KEK is still in the keyring; (b) the same documents after the old KEK is destroyed without rewrapping; (c) the same documents after a lazy rewrap on read, followed by destruction of the old KEK.

**Model answer.**
(a) Yes. The header names the KEK version, and the keyring still holds that version. [3]
(b) No. The wrapped data keys can no longer be unwrapped; destroying a KEK is crypto-shredding. [3]
(c) Only the documents that were read, and therefore rewrapped, before destruction decrypt. Cold documents are lost unless a background rewrap job ran first. [3]
Lesson: track rewrap progress as a metric before retiring a key (L300 #12). [1]

## Q4 - Design critique (14 marks)
A team implements hybrid post-quantum key exchange (X25519MLKEM768). The client concatenates both shares (1,216 bytes), but "for robustness" it accepts a 32-byte server share and then continues with X25519 only. Signatures stay Ed25519-only. Critique the design and propose fixes, quantifying the costs where you can.

**Model answer.**
- **Silent downgrade.** An on-path attacker truncates the server share to 32 bytes, and the session becomes classical, so it can be recorded now and decrypted later by a quantum attacker. Fix: the client MUST check the share length and abort (RFC 10024 §4.2, L400 #18), and any classical-only session should raise an alert. [5]
- **Byte costs.** The client share is 1,216 B and the server share 1,120 B (2,336 B total), against 64 B for X25519 alone. Large ClientHellos can trip middleboxes, so roll out gradually and watch error rates. [3]
- **Signatures.** Ed25519-only authentication is acceptable for now, because a signature forged later cannot affect a session that has already ended; key exchange migrates first. Plan for ML-DSA, whose signatures are 3,309 B for ML-DSA-65 versus 64 B for Ed25519, with dual signing during the transition. The verifier's policy, not the message, decides which signatures are required (L400 #17). [4]
- **Agility.** Algorithm identifiers belong in a registry with a policy, and a fitness function should check this (L400 #17). [2]

## Q5 - Short explanation (10 marks)
(a) Why do short-lived certificates reduce the need for revocation (L300 #13)? (4)
(b) What does signing a release artefact prove and not prove, and why should verifiers pin the signer identity (L300 #14)? (6)

**Model answer.**
(a) A compromised key is only usable until the certificate expires, so the window shrinks to hours or days. Revocation checking (CRL/OCSP) is often soft-fail and slow, and automated renewal replaces it for most cases. [4]
(b) A signature proves the artefact is unchanged since the holder of the key signed it. It does not prove the code is benign, that it was built from the claimed source, or that the signer was the intended one. Verifiers therefore pin the expected identity or key, and check the provenance (build attestation) and the transparency log; otherwise any validly signed artefact passes. [6]

## Q6 - Calculation (10 marks)
(a) The generic cost of discrete log in a prime-order group of size about 2^64, and in one of about 2^256. (3)
(b) The toy Regev decoding threshold for q = 3329, and the worst-case noise for 32 samples with |eᵢ| ≤ 2. (3)
(c) The entropy of a uniformly random 6-digit passcode, and why it matters in device encryption. (4)

**Model answer.**
(a) About 2^32 and about 2^128 group operations (√q; Shoup's generic lower bound). [3]
(b) Threshold 832; worst-case noise 64, so decryption never fails. [3]
(c) log₂ 10^6 ≈ 19.9 bits. Guess-limiting in hardware or the OS, not the AES key, protects the device (lesson 26 case). [4]

## Q7 - Ethics (12 marks)
You maintain an internal library and discover that a widely used open-source dependency verifies JWT signatures with the algorithm from the token header. Write a disclosure and remediation plan that covers who, how, what, when, and what you publish. Cite the relevant standard or guide and two ACM Code principles.

**Model answer.**
- **Internal response.** Pin the algorithm in your own code now, which is a mitigation that does not reveal the bug. [2]
- **Report.** Report privately through the project's security policy (SECURITY.md or a private advisory) with a minimal reproduction, the impact (forged tokens) and a suggested fix. [3]
- **Timeline.** Agree a timeline, commonly about 90 days and adjustable, and escalate to a coordinator such as CERT/CC if there is no response (CERT Guide to CVD; ISO/IEC 29147 for the vendor side). [3]
- **Publication.** Request a CVE and coordinate a release and an advisory with credit. [2]
- **ACM principles.** 2.9 (secure systems) and 1.2 (avoid harm: do not publish an exploit before a fix); 2.8 (no testing on others' systems without authorisation). [2]

## Q8 - Capstone design (20 marks)
Design the key hierarchy and threat model of an encrypted document service in which multi-tenant users share documents. It must support key rotation, revocation of a user, a post-quantum migration path and audit. Justify each choice with a lesson. Name one fitness function and one metric that would reveal failure.

**Model answer.** A strong answer covers these elements (L400 #22 capstone):
- **Envelope encryption:** a per-document data key, wrapped under a per-tenant KEK that is held in hardware-style storage and non-exportable (L300 #12, L400 #19). [4]
- **AEAD with AAD:** bind the document ID, the tenant and the header version as associated data (L100 #4; lesson 25 IND-CCA). [3]
- **Sharing:** wrap the data key to the recipient with HPKE using MLKEM768_X25519. Revoking a user means re-keying the documents they could read, because forward-looking revocation needs a new data key (L400 #18, #20). [4]
- **Signatures and audit:** signed audit records, with dual signing during the PQ transition and verifier policy deciding what is required (L400 #17). [3]
- **Threat model:** a STRIDE table plus an attack tree tied to tests (L400 #21). [3]
- **Fitness function:** for example "no primitive imports outside the registry" (agility lint). **Metric:** for example envelopes by algorithm or the count of unrotated KEKs. [3]
