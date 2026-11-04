"""Call a running server.py and check each response against openapi.json.
Run (second terminal): python client_demo.py [port]"""
import sys

from contract_check import check, load_spec
from test_contract import call

base = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 8000}"
spec = load_spec()
for method, path, body in [("GET", "/health", None),
                           ("POST", "/loans", {"bookId": "b1", "memberId": "m1"}),
                           ("POST", "/loans", {"bookId": "b1", "memberId": "m2"}),
                           ("GET", "/loans/1", None)]:
    status, payload = call(base, method, path, body)
    problems = check(spec, method, path, status, payload)
    print(f"{method:<4} {path:<9} -> {status} {payload}  contract: {'OK' if not problems else problems}")
