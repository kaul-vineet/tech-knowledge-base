"""Library Loans' catalogue client (the CONSUMER). It reads only `title` and `available` from the response."""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass


class BookNotFound(Exception):
    pass


@dataclass(frozen=True)
class Book:
    title: str
    available: bool


class CatalogueClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def book(self, book_id):
        try:
            with urllib.request.urlopen(f"{self.base_url}/books/{book_id}", timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise BookNotFound(book_id) from None
            raise
        return Book(title=body["title"], available=body["available"])  # the two fields this consumer needs


def loan_receipt(client, member_id, book_id):
    book = client.book(book_id)
    if not book.available:
        return f"{member_id}: '{book.title}' is on loan, you are on the waiting list"
    return f"{member_id}: you borrowed '{book.title}'"
