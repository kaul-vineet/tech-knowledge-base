"""Consumer side (Library Loans): the real client runs against a mock provider; the run writes the contract."""
import pathlib
import unittest

from consumer import Book, BookNotFound, CatalogueClient, loan_receipt
from contract import ContractBuilder, like

HERE = pathlib.Path(__file__).resolve().parent
CONSUMER_VERSION = "1.4.0"  # the consumer's own release; the contract file records it


def loans_contract():
    return (ContractBuilder("loans-service", "catalogue-service", CONSUMER_VERSION)
            .interaction("a request for an existing book", "book b1 exists", "GET", "/books/b1", 200,
                         {"id": "b1", "title": like("Dune"), "available": like(True)})
            .interaction("a request for a missing book", "no books", "GET", "/books/b404", 404, {}))


class StubClient:  # hand-written stub: fast, but it only knows what WE think the provider returns
    def book(self, book_id):
        return Book(title="Dune", available=True)


class ConsumerUnitTest(unittest.TestCase):
    def test_receipt_with_a_stub(self):
        self.assertEqual(loan_receipt(StubClient(), "m1", "b1"), "m1: you borrowed 'Dune'")


class ConsumerContractTest(unittest.TestCase):
    def test_client_against_the_mock_provider_and_write_the_contract(self):
        builder = loans_contract()
        with builder.mock_provider() as url:
            client = CatalogueClient(url)
            self.assertEqual(client.book("b1"), Book("Dune", True))
            with self.assertRaises(BookNotFound):
                client.book("b404")
        path = builder.write(HERE / "contracts")  # versioned in the repo; the provider build reads it
        self.assertEqual(path.name, "loans-service--catalogue-service.json")

    def test_mock_fails_when_an_interaction_is_never_exercised(self):
        with self.assertRaises(AssertionError):
            with loans_contract().mock_provider() as url:
                CatalogueClient(url).book("b1")


if __name__ == "__main__":
    unittest.main()
