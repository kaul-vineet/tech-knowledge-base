import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

import server
from contract_check import check, load_spec


def call(base, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


class SpecShapeTest(unittest.TestCase):
    def test_required_top_level_fields(self):
        spec = load_spec()
        self.assertTrue(spec["openapi"].startswith("3.1."))
        self.assertTrue(spec["info"]["title"] and spec["info"]["version"])
        self.assertTrue(spec["paths"])


class ContractTest(unittest.TestCase):
    # (method, path, body, expected status) - together they hit every declared response
    CASES = [
        ("GET", "/health", None, 200),
        ("POST", "/loans", {"bookId": "b1", "memberId": "m1"}, 201),
        ("POST", "/loans", {"bookId": "b1", "memberId": "m2"}, 409),
        ("POST", "/loans", {"bookId": "b2"}, 400),
        ("GET", "/loans/1", None, 200),
        ("GET", "/loans/999", None, 404),
    ]

    def setUp(self):
        server.LOANS.clear()
        self.spec = load_spec()
        self.httpd = HTTPServer(("127.0.0.1", 0), server.LoansApi)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.base = f"http://127.0.0.1:{self.httpd.server_port}"

    def test_responses_match_spec(self):
        for method, path, body, expected in self.CASES:
            with self.subTest(method=method, path=path, expected=expected):
                status, payload = call(self.base, method, path, body)
                self.assertEqual(status, expected)
                self.assertEqual(check(self.spec, method, path, status, payload), [])

    def test_every_declared_response_is_exercised(self):
        declared = {(m.upper(), t, s) for t, item in self.spec["paths"].items()
                    for m, op in item.items() for s in op["responses"]}
        exercised = {("GET", "/health", "200"), ("POST", "/loans", "201"), ("POST", "/loans", "409"),
                     ("POST", "/loans", "400"), ("GET", "/loans/{loanId}", "200"),
                     ("GET", "/loans/{loanId}", "404")}
        self.assertEqual(declared, exercised)


class CheckerCatchesDriftTest(unittest.TestCase):
    def test_undeclared_status_and_bad_body_are_reported(self):
        spec = load_spec()
        self.assertIn("not declared", check(spec, "GET", "/loans/1", 500, {})[0])
        problems = check(spec, "GET", "/loans/1", 200, {"id": "1", "bookId": "b1", "status": "lost"})
        self.assertEqual(len(problems), 3)  # missing memberId, id not integer, status not in enum


if __name__ == "__main__":
    unittest.main()
