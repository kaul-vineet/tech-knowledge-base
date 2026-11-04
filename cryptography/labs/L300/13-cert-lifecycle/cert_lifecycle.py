"""Certificate lifecycle on a simulated clock: short-lived certs, expiry metrics, CRL revocation, clock skew.
Reuses lesson 9's local CA. The Server below never renews (the fault); the build task adds a jittered renewal loop."""
import datetime as dt
import json
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "L200" / "09-local-ca"))  # after this folder: no name clashes
import local_ca  # noqa: E402
from cryptography import x509  # noqa: E402
from cryptography.hazmat.primitives import hashes  # noqa: E402

SEED = 13
HOUR = dt.timedelta(hours=1)
LIFETIME = dt.timedelta(hours=160)  # short-lived: like Let's Encrypt's 160-hour "shortlived" profile
T0 = local_ca.NOW + dt.timedelta(days=1)  # simulated clock starts after the root became valid


def issue(ca_key, ca, at, backdate=HOUR):
    start = at - backdate  # backdated notBefore tolerates clients whose clock runs a little slow
    return local_ca.issue_server(ca_key, ca, days=LIFETIME / dt.timedelta(days=1), not_before=start)[1]


def handshake_ok(cert, ca, client_time) -> bool:
    try:
        local_ca.verify(cert, [ca], "localhost", at=client_time)
        return True
    except x509.verification.VerificationError:
        return False


class Server:
    """Loads one certificate at start-up. BUG on purpose: tick() never renews it."""

    def __init__(self, ca_key, ca, now, rng):
        self.ca_key, self.ca, self.rng = ca_key, ca, rng
        self.cert, self.renewals, self.alerts, self.log = issue(ca_key, ca, now), 0, 0, print

    def tick(self, now, ca_up=True):
        pass


def simulate(server_cls, days=10, seed=SEED, ca_down=range(0), log=print):
    ca_key, ca = local_ca.make_root()
    srv = server_cls(ca_key, ca, T0, random.Random(seed))  # seeded: renewal jitter is reproducible
    srv.log = log
    failures = []
    for h in range(days * 24):
        now = T0 + h * HOUR
        srv.tick(now, ca_up=h not in ca_down)  # injected fault: the CA is unreachable during ca_down hours
        left = (srv.cert.not_valid_after_utc - now) / HOUR
        ok = handshake_ok(srv.cert, ca, now)
        if not ok:
            failures.append(h)
        if h % 24 == 0 or (not ok and len(failures) == 1):  # metric line: what a dashboard would scrape
            log(json.dumps({"hour": h, "metric": "cert_expires_in_hours", "value": round(left, 1),
                            "handshake": "ok" if ok else "FAIL", "renewals": srv.renewals}))
    return failures, srv


def make_crl(ca_key, ca, revoked_serials, now, valid_for=dt.timedelta(hours=24)):
    b = (x509.CertificateRevocationListBuilder().issuer_name(ca.subject)
         .last_update(now).next_update(now + valid_for))  # thisUpdate / nextUpdate (RFC 5280 s5.1.2.4-5)
    for serial in revoked_serials:
        b = b.add_revoked_certificate(
            x509.RevokedCertificateBuilder().serial_number(serial).revocation_date(now)
            .add_extension(x509.CRLReason(x509.ReasonFlags.key_compromise), critical=False).build())
    return b.sign(ca_key, hashes.SHA256())


def check_revocation(cert, crl, ca, now) -> str:
    if crl.issuer != ca.subject or not crl.is_signature_valid(ca.public_key()):
        return "bad CRL"  # an unsigned or foreign CRL must not decide anything
    if now > crl.next_update_utc:
        return "stale CRL"  # fail closed or alert: an old CRL may miss recent revocations
    entry = crl.get_revoked_certificate_by_serial_number(cert.serial_number)
    return "good" if entry is None else f"revoked ({entry.extensions.get_extension_for_class(x509.CRLReason).value.reason.name})"


if __name__ == "__main__":
    failures, srv = simulate(Server, days=8)
    print(f"static server: first failed handshake at hour {failures[0]}, {len(failures)} failed hours of {8 * 24}")

    ca_key, ca = local_ca.make_root()
    cert = issue(ca_key, ca, T0)
    print("lifetime:", (cert.not_valid_after_utc - cert.not_valid_before_utc) / HOUR, "h, notBefore backdated 1 h")
    crl = make_crl(ca_key, ca, [cert.serial_number], T0)
    print("CRL check now:        ", check_revocation(cert, crl, ca, T0))
    print("CRL check other cert: ", check_revocation(issue(ca_key, ca, T0), crl, ca, T0))
    print("CRL check 25 h later: ", check_revocation(cert, crl, ca, T0 + 25 * HOUR))

    slow_client = T0 - dt.timedelta(minutes=5)  # client clock 5 minutes behind the issuer
    print("skew 5 min, notBefore = issue time:", handshake_ok(issue(ca_key, ca, T0, backdate=dt.timedelta(0)), ca, slow_client))
    print("skew 5 min, notBefore backdated 1 h:", handshake_ok(cert, ca, slow_client))
