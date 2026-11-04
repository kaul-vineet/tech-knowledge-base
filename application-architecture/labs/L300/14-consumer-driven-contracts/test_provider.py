"""Provider side (catalogue): its own unit test, plus verification of every consumer contract in contracts/."""
import json
import pathlib
import unittest
import urllib.request

import provider
from contract import verify_provider

HERE = pathlib.Path(__file__).resolve().parent


class ProviderUnitTest(unittest.TestCase):
    def test_get_book(self):
        server, url = provider.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        with urllib.request.urlopen(url + "/books/b1", timeout=5) as resp:
            self.assertEqual(json.loads(resp.read()), {"id": "b1", "title": "Dune", "available": True})


class ProviderVerificationTest(unittest.TestCase):
    def test_every_consumer_contract_holds(self):
        server, url = provider.start(states=True)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        contracts = sorted((HERE / "contracts").glob("*.json"))
        self.assertTrue(contracts, "no contracts in contracts/")
        for path in contracts:
            self.assertEqual(verify_provider(path, url), [], path.name)


if __name__ == "__main__":
    unittest.main()
