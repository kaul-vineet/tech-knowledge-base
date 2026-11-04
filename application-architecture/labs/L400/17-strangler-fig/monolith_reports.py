"""Old monolith report that calls the legacy fine code directly. Existing caller: on the fitness baseline
(legacy_callers.json). It may be migrated away; it must not be copied."""
from legacy_monolith import calculate_fine


def fines_total(loans):
    return sum(float(calculate_fine(days, kind)) for days, kind in loans)
