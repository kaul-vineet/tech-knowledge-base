"""Build task solution: renew before expiry on a jittered schedule, retry while the CA is down, alert on low margin."""
import json

from cert_lifecycle import HOUR, LIFETIME, Server as _Static, issue

WINDOW = (0.60, 0.72)  # renew somewhere between 60 % and 72 % of the lifetime (about 1/3 left, like ACME clients)
ALERT_BELOW = LIFETIME / 4  # page someone when less than 40 h are left


def next_renewal(cert, rng):
    """Uniform random time inside the renewal window (RFC 9773 ARI clients do the same with the server's window)."""
    start = cert.not_valid_before_utc
    return start + LIFETIME * rng.uniform(*WINDOW)  # jitter: a fleet does not renew in the same minute


class Server(_Static):
    def __init__(self, ca_key, ca, now, rng):
        super().__init__(ca_key, ca, now, rng)
        self.renew_at = next_renewal(self.cert, rng)

    def tick(self, now, ca_up=True):
        if now >= self.renew_at:
            if ca_up:
                self.cert = issue(self.ca_key, self.ca, now)  # hot swap: new connections get the new cert
                self.renewals += 1
                self.renew_at = next_renewal(self.cert, self.rng)
            else:
                self.renew_at = now + HOUR  # retry next hour; keep serving the still-valid old cert
        if self.cert.not_valid_after_utc - now < ALERT_BELOW:
            self.alerts += 1
            self.log(json.dumps({"alert": "cert_expiry_soon", "hours_left": round((self.cert.not_valid_after_utc - now) / HOUR, 1)}))


if __name__ == "__main__":
    from cert_lifecycle import simulate

    failures, srv = simulate(Server, days=21, log=lambda line: None)
    print(f"renewing server, 21 days: {len(failures)} failed handshakes, {srv.renewals} renewals, {srv.alerts} alerts")
    alerts = []
    failures, srv = simulate(Server, days=21, ca_down=range(90, 125), log=lambda line: alerts.append(line) if "alert" in line else None)
    print(f"CA down hours 90-124: {len(failures)} failed handshakes, {srv.renewals} renewals, {srv.alerts} alert lines")
    print("first alert:", alerts[0])
