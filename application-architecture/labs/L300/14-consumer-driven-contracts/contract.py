"""Consumer-driven contracts, stdlib only (lesson 14 lab code). Same flow as Pact, NOT Pact's file format.

Consumer side: declare interactions -> run the real client against a mock provider -> write contracts/*.json.
Provider side: replay every interaction against the real provider and compare. Weakness (failureLab):
verify_provider() only compares status codes.
"""
import json
import pathlib
import threading
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def like(example):
    """Matcher: any value of the same type as `example` (the consumer cares about the field, not the value)."""
    return {"$like": example}


def _example(body, rules, path="$"):  # strip matchers -> (example body, {json path: "type"})
    if isinstance(body, dict) and "$like" in body:
        rules[path] = "type"
        return body["$like"]
    if isinstance(body, dict):
        return {key: _example(value, rules, f"{path}.{key}") for key, value in body.items()}
    return body


class ContractBuilder:
    def __init__(self, consumer, provider, consumer_version):
        self.contract = {"consumer": consumer, "provider": provider, "interactions": [],
                         "metadata": {"format": "lesson-14 contract v1", "consumerVersion": consumer_version}}

    def interaction(self, description, state, method, path, status, body):
        rules = {}
        response = {"status": status, "body": _example(body, rules), "matchingRules": rules}
        self.contract["interactions"].append({"description": description, "providerState": state,
                                              "request": {"method": method, "path": path}, "response": response})
        return self

    @contextmanager
    def mock_provider(self):
        """Serve the declared responses; fail if the consumer skipped an interaction or sent an unexpected one."""
        routes = {(i["request"]["method"], i["request"]["path"]): i for i in self.contract["interactions"]}
        used, unexpected = set(), []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                found = routes.get(("GET", self.path))
                (used.add(("GET", self.path)) if found else unexpected.append(f"GET {self.path}"))
                status, body = (found["response"]["status"], found["response"]["body"]) if found else (500, {})
                data = json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
        missing = sorted(set(routes) - used)
        if unexpected or missing:
            raise AssertionError(f"mock provider: unexpected {unexpected}, never called {missing}")

    def write(self, folder):
        path = pathlib.Path(folder) / f"{self.contract['consumer']}--{self.contract['provider']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path


def _request(base_url, method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(base_url + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8") or "{}")


def verify_provider(contract_path, provider_url):
    """Replay each interaction against the REAL provider (after setting its state). Returns a list of problems."""
    contract = json.loads(pathlib.Path(contract_path).read_text(encoding="utf-8"))
    problems = []
    for item in contract["interactions"]:
        _request(provider_url, "POST", "/_contract/state", {"state": item["providerState"]})
        status, body = _request(provider_url, item["request"]["method"], item["request"]["path"])
        expected = item["response"]
        if status != expected["status"]:  # weakness: the body is never compared
            problems.append(f"{item['description']}: status {status}, contract says {expected['status']}")
    return problems
