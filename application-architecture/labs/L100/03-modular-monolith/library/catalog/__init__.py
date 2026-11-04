"""Catalog module - PUBLIC interface. Other modules may import only what is listed here."""
from .internal import store

__all__ = ["is_available", "set_on_loan"]


def is_available(book_id):
    return store.BOOKS.get(book_id) == "on_shelf"


def set_on_loan(book_id, on_loan):
    store.BOOKS[book_id] = "on_loan" if on_loan else "on_shelf"
