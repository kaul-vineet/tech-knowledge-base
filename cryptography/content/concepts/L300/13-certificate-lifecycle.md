## Why it matters
Certificates are getting shorter. Under the CA/Browser Forum schedule, public TLS certificates may last at most 200 days from March 2026, 100 days from 2027 and 47 days from 2029, and Let's Encrypt already offers 160-hour certificates. A service that loads its certificate once goes dark on a predictable date. Renewal must be a monitored loop, not a calendar reminder.

## Mental model
A certificate is a **parking ticket with an end time**. Buy the next one early, at a slightly random moment, so the fleet doesn't queue at once. A CRL is the **list of cancelled tickets** the attendant carries; it is only as fresh as its print time.

```
issue ──────────── renew window (60-72 %) ───── alert (<25 % left) ──── notAfter
  │ notBefore backdated 1 h (clock skew)                                  │ expired: handshakes FAIL
CRL: thisUpdate ── nextUpdate (stale after this) ── revoked serials + reason
```

## How it works
1. **Short-lived certs and metrics.** The lab issues 160-hour leaf certificates on a simulated clock. Each simulated hour emits a JSON metric `cert_expires_in_hours`; the static server's value falls to zero, then handshakes fail → see lab steps 1-2.
2. **Revocation with a CRL.** The CA signs a list of revoked serial numbers with a reason and thisUpdate/nextUpdate times. The checker verifies issuer and signature, refuses a CRL past nextUpdate ("stale CRL"), then looks up the serial. OCSP answers the same question per certificate (good/revoked/unknown) → see lab step 3.
3. **Clock skew.** A client whose clock runs 5 minutes slow rejects a certificate whose notBefore is "now". Backdating notBefore by one hour absorbs that skew → see lab step 4.
4. **Renewal with jitter.** The fixed server picks a uniform random time in the 60-72 % window of the lifetime. If the CA is unreachable it retries hourly, swaps the new certificate in, and logs an alert line once less than a quarter of the lifetime remains → see lab step 6.
5. **Proof.** `test_build_task.py` runs 21 simulated days, a 35-hour CA outage and a 50-server jitter check against your server → see lab step 6.

Worked example (one lab run): the static server's first failed handshake was at hour 160, with 32 failed hours out of 192. The renewing server ran 21 days with 0 failures and 4 renewals. With the CA down for hours 90-124 it still had 0 failures and emitted 6 alert lines. Renewal times for 100 servers fell into 20 distinct hours instead of 1. A 1-hour backdate accepted clients 59 minutes slow but not 61.

## Failure modes
- **Expired certificate still served.** A missing reload or a silently failing cron; a falling expiry metric shows it days before clients do.
- **Thundering herd.** Every server renews at once and the CA rate-limits them; jitter spreads the load.
- **Stale or forged CRL.** The checker must verify the CRL's signature and freshness, and decide in advance whether a stale CRL fails open or closed.
- **Skew.** "Not yet valid" right after issuance means a slow client clock or no backdate.

## Common mistakes
- Renewing at a fixed "30 days before expiry": broken once lifetimes drop below 30 days.
- Writing the new certificate to disk without reloading the process.
- Treating `is_signature_valid()` as "trusted": the CRL must also come from the right issuer and be current.
