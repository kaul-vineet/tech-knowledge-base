"""Key ceremony basics (learning version): generate a signing key INSIDE the token under dual control, with witnesses,
and leave a verifiable transcript. Roles: the security officer (SO) initialises the token but cannot use keys; a key
custodian logs in as USER; at least two witnesses must be present. The transcript ends with a proof of possession:
the new key signs the transcript hash, and anyone can verify it with the exported public key."""
import hashlib
import json

from cryptography.hazmat.primitives import serialization as ser

from solution_nonexportable import CKA_VALUE, CKM_EDDSA, SoftToken

MIN_WITNESSES = 2


def run_ceremony(custodian: str, witnesses: list, label: str = "release-signing-2026"):
    if len(set(witnesses)) < MIN_WITNESSES or custodian in witnesses:
        raise ValueError(f"need {MIN_WITNESSES} distinct witnesses who are not the custodian")
    steps = [{"step": 1, "do": "SO initialises token, sets USER PIN (out of band)", "by": "SO", "seen_by": witnesses}]
    token = SoftToken("ceremony", so_pin="so-demo-1234", user_pin="user-demo-5678")  # demo PINs only
    s = token.open_session()
    s.login("USER", "user-demo-5678")
    pub, priv = s.generate_key_pair(CKM_EDDSA, label)  # non-exportable: enforced by the token
    pub_der = s.get_attribute_value(pub, CKA_VALUE)
    fingerprint = hashlib.sha256(pub_der).hexdigest()
    steps.append({"step": 2, "do": f"generate {label} in token (CKM_EDDSA, non-exportable)", "by": custodian, "seen_by": witnesses})
    steps.append({"step": 3, "do": "export PUBLIC key and read fingerprint aloud", "sha256": fingerprint, "seen_by": witnesses})
    digest = hashlib.sha256(json.dumps(steps, sort_keys=True).encode()).digest()
    pop = s.sign(priv, CKM_EDDSA, digest)  # proof of possession over the whole transcript
    s.logout()
    return {"steps": steps, "transcript_sha256": digest.hex(), "pop_sig": pop.hex(), "public_key_der": pub_der.hex()}


def verify_ceremony(record: dict) -> bool:
    digest = hashlib.sha256(json.dumps(record["steps"], sort_keys=True).encode()).digest()
    pub = ser.load_der_public_key(bytes.fromhex(record["public_key_der"]))
    try:
        pub.verify(bytes.fromhex(record["pop_sig"]), digest)
    except Exception:
        return False
    return digest.hex() == record["transcript_sha256"] and hashlib.sha256(bytes.fromhex(record["public_key_der"])).hexdigest() == record["steps"][2]["sha256"]


if __name__ == "__main__":
    rec = run_ceremony("custodian-a", ["witness-b", "witness-c"])
    for step in rec["steps"]:
        print(json.dumps(step))
    print("transcript verifies:", verify_ceremony(rec))
    rec["steps"][1]["seen_by"] = ["witness-b"]  # someone edits the record afterwards
    print("edited transcript verifies:", verify_ceremony(rec))
    try:
        run_ceremony("custodian-a", ["custodian-a", "witness-b"])
    except ValueError as e:
        print("custodian as own witness:", e)
