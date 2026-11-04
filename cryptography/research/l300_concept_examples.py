"""Computes every number quoted in the L300 concept notes (content/concepts/L300/*.md).
Run from this folder: python l300_concept_examples.py > l300_concept_examples.out.txt"""
import io
import random
import sys
import tempfile
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs" / "L300"
QUIET = lambda line: None  # noqa: E731


def lab(folder):
    sys.path.insert(0, str(LABS / folder))
    for name in ("solution_retire", "solution_renewal", "solution_strict", "solution_redact"):
        sys.modules.pop(name, None)


lab("12-envelope-rotation")
import envelope as env  # noqa: E402
import solution_retire  # noqa: E402

print("== 12 envelope ==")
ring = env.Keyring()
store = {f"order-{i}": env.seal(ring, b"x" * 20, f"order-{i}") for i in range(1, 7)}
print("wrapped DEK bytes:", len(env.base64.b64decode(store["order-1"]["wdek"])))
ring.rotate()
try:
    env.rewrap_job(ring, store, log=QUIET, crash_after=1)
except RuntimeError as e:
    print("crash:", e, env.count_by_kid(store))
try:
    solution_retire.retire(ring, store, 1)
except env.KeyInUse as e:
    print("hardened retire:", e)
env.retire(ring, store, 1)
print("naive retire:", env.try_all(ring, store))

lab("13-cert-lifecycle")
import cert_lifecycle as cl  # noqa: E402
import solution_renewal as sr  # noqa: E402

print("== 13 cert lifecycle ==")
f, _ = cl.simulate(cl.Server, days=8, log=QUIET)
print("static: first failure hour", f[0], "failed hours", len(f))
f, srv = cl.simulate(sr.Server, days=21, log=QUIET)
print("renewing 21 d: failures", len(f), "renewals", srv.renewals)
f, srv = cl.simulate(sr.Server, days=21, ca_down=range(90, 125), log=QUIET)
print("CA down 90-124: failures", len(f), "alerts", srv.alerts)
print("window hours:", 160 * sr.WINDOW[0], "-", 160 * sr.WINDOW[1], "| alert below", sr.ALERT_BELOW)
ca_key, ca = cl.local_ca.make_root()
cert = cl.issue(ca_key, ca, cl.T0)
hours = {round((sr.next_renewal(cert, random.Random(s)) - cert.not_valid_before_utc) / cl.HOUR) for s in range(100)}
print("100 servers, distinct renewal hours with jitter:", len(hours))
for minutes in (59, 61):
    print(f"client {minutes} min slow, 1 h backdate:", cl.handshake_ok(cert, ca, cl.T0 - cl.dt.timedelta(minutes=minutes)))

lab("14-supply-chain-signing")
import release_sign as rs  # noqa: E402

print("== 14 supply chain ==")
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    rs.build_artifacts(d)
    print("core.py sha256:", rs.digest(d / "app" / "core.py"), "size", (d / "app" / "core.py").stat().st_size)
    print("files:", rs.files_in(d))
    print("seeded victim:", rs.tamper(d))

lab("15-testable-misuse")
import timing_demo as td  # noqa: E402
import wycheproof_check as wc  # noqa: E402

print("== 15 misuse ==")
rows = wc.run()
print("vectors:", len(rows), "lenient failures:", [r[1] for r in wc.failures(rows)])
e, l_ = td.experiment(td.naive_equal)
print(f"naive timing early {e:.0f} ns late {l_:.0f} ns ratio {l_ / e:.2f}")
import hmac  # noqa: E402

e, l_ = td.experiment(hmac.compare_digest)
print(f"compare_digest early {e:.0f} ns late {l_:.0f} ns ratio {l_ / e:.2f}")

lab("16-secrets-handling")
import secrets_app as app  # noqa: E402

print("== 16 secrets ==")
buf = io.StringIO()
key = app.Secret("sk_demo_" + "".join(random.Random(1).choice("abcdef0123456789") for _ in range(32)))
app.handle_request(app.json_logger(buf, "x"), key, 1, debug=True)
print("findings:", [(n, k) for n, k, _ in app.scan_log(buf.getvalue(), known=[key.reveal()])])
keys = app.ApiKeys("old")
keys.rotate("new", now=0, grace_s=86400)
print("old key at 23 h:", keys.check("old", 23 * 3600), "| at 25 h:", keys.check("old", 25 * 3600))
