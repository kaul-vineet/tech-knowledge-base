"""Overdue rules: pure domain code (no database, no HTTP). The import-boundary gate keeps it that way."""
from datetime import date

LOAN_DAYS = 21
FINE_PER_DAY = 0.25


def days_overdue(due: date, today: date) -> int:
    return max(0, (today - due).days)


def fine(days: int) -> float:
    return round(min(days * FINE_PER_DAY, 10.0), 2)  # capped at 10.00
