"""Loans module - PUBLIC interface."""
from .internal.rules import borrow, give_back

__all__ = ["borrow", "give_back"]
