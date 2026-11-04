"""Lesson 14 with Pact (pact-python 4.2.0) - the industry tool for the same flow. CI only (pending-ci).

Skipped unless LOANS_PACT=1 and pact-python is installed:  pip install -r ../requirements-ci.txt
Written against the pact-python 4.x docs (docs.pact.io/implementation_guides/python); not run in the sandbox.
"""
import os
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from consumer import Book, CatalogueClient  # noqa: E402
import provider  # noqa: E402

try:
    from pact import Pact, Verifier, match
except ImportError:  # pact-python not installed (the sandbox and a plain lesson-1 venv)
    Pact = None

PACT_DIR = HERE / "pacts"
ENABLED = os.environ.get("LOANS_PACT") == "1" and Pact is not None


@unittest.skipUnless(ENABLED, "set LOANS_PACT=1 and pip install pact-python==4.2.0")
class PactTest(unittest.TestCase):
    def test_1_consumer_writes_the_pact(self):
        pact = Pact("loans-service", "catalogue-service").with_specification("V4")
        (pact.upon_receiving("a request for an existing book").given("book b1 exists")
         .with_request("GET", "/books/b1").will_respond_with(200)
         .with_body({"id": "b1", "title": match.like("Dune"), "available": match.like(True)},
                    content_type="application/json"))
        with pact.serve() as srv:
            self.assertEqual(CatalogueClient(str(srv.url)).book("b1"), Book("Dune", True))
        pact.write_file(PACT_DIR)
        self.assertTrue(list(PACT_DIR.glob("*.json")))

    def test_2_provider_verifies_the_pact(self):
        server, url = provider.start(states=True)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        (Verifier("catalogue-service").add_source(str(PACT_DIR)).add_transport(url=url)
         .state_handler(url + "/_contract/state", body=True).verify())


if __name__ == "__main__":
    unittest.main()
