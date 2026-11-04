"""Serve the capstone's member-portal API on 127.0.0.1 for manual exploration (Bruno, curl). Ctrl+C to stop.

Run: python serve.py [port]   (default 8022). Seeds lib00/m1 with one loan. Send the caller as an X-Subject header:
     X-Subject: {"id": "m1", "tenant": "lib00", "roles": ["member"]}
"""
import sys
import time

import loans_service
from http_api import MEMBER, start
from reuse import POLICY_FIXED, fines_fixed, rego_lite, strangler


def make_service():
    pdp = rego_lite.DecisionPoint(rego_lite.load_policy(POLICY_FIXED))
    fines = strangler.Facade(strangler.LegacyFines(), strangler.ServiceFines(fn=fines_fixed.fine_for), mode="service")
    service = loans_service.LoansService(pdp, fines)
    service.borrow(MEMBER, "lib00", "m1", "adult", "b1")
    return service


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8022
    server, url = start(make_service, port=port)
    print(f"serving {url}/tenants/lib00/members/m1/loans (Ctrl+C to stop)", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
