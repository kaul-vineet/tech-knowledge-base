"""The Library Loans monolith (legacy). Not lesson code: this is the thing being strangled.

calculate_fine() is the module we extract into its own service. Quirks the new service must reproduce:
2 grace days, 0.25 per chargeable day, students pay half, cap 10.00, cents rounded HALF-UP.
"""
from decimal import ROUND_HALF_UP, Decimal


def calculate_fine(days_late, member_type):
    chargeable = max(0, days_late - 2)
    fine = Decimal("0.25") * chargeable
    if member_type == "student":
        fine = fine / 2
    fine = min(fine, Decimal("10.00"))
    return str(fine.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def loan_statement(member_id, member_type, days_late):
    """Old monolith code that still calls calculate_fine directly (a known, allow-listed caller)."""
    return f"member {member_id}: {days_late} days late, fine {calculate_fine(days_late, member_type)}"
