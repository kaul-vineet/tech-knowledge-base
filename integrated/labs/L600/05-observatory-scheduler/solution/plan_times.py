"""Solution (build task): agent-written times are converted when zoned and refused when naive."""
import re
from datetime import datetime

from timeutil import UtcInstant

ISO_WITH_ZONE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})$")


def parse_plan_time(text):
    """'2026-11-19T13:20:00Z' or '...+05:30' -> UtcInstant; no zone -> ValueError (never guess a zone)."""
    text = text.strip()
    if not ISO_WITH_ZONE.match(text):
        raise ValueError(f"{text!r}: need ISO 8601 with 'Z' or an explicit UTC offset")
    return UtcInstant.from_aware(datetime.fromisoformat(text.replace("Z", "+00:00")))
