"""Build task check (lesson 14): verify_provider() must catch a renamed or retyped field, and allow extra fields.

By default this checks solution/contract.py. To check your edited contract.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

import provider

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("contract.py" if os.environ.get("CHECK_MINE") else "solution/contract.py")
spec = importlib.util.spec_from_file_location("contract_under_test", TARGET)
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)
CONTRACT = HERE / "contracts" / "loans-service--catalogue-service.json"


class VerifierTest(unittest.TestCase):
    def verify(self, **provider_options):
        server, url = provider.start(states=True, **provider_options)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return ct.verify_provider(CONTRACT, url)

    def test_unchanged_provider_passes(self):
        self.assertEqual(self.verify(), [])

    def test_renamed_field_fails(self):
        self.assertEqual(self.verify(title_field="name"),
                         ["a request for an existing book: $.title: missing (the consumer reads it)"])

    def test_retyped_field_fails_and_extra_field_passes(self):
        original = provider.book_body
        provider.book_body = lambda book_id, book, title_field="title": {
            **original(book_id, book, title_field), "available": "yes", "isbn": "978-0"}
        self.addCleanup(setattr, provider, "book_body", original)
        self.assertEqual(self.verify(), ["a request for an existing book: $.available: expected bool, got str 'yes'"])


if __name__ == "__main__":
    unittest.main()
