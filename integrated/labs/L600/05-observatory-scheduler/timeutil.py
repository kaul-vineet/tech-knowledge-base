"""Typed time at the astronomy <-> scheduler seam: every instant that reaches sky maths is a UtcInstant.

Rules (ADR 0001): naive datetimes are refused; aware ones are CONVERTED with astimezone(), never relabelled with
replace(tzinfo=...); text crossing a boundary (agent plans, logs) is ISO 8601 with 'Z' or an explicit offset (plan_times.py).
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import _kb

UTC = timezone.utc


@dataclass(frozen=True, order=True)
class UtcInstant:
    dt: datetime

    def __post_init__(self):
        if self.dt.tzinfo is None:
            raise TypeError("naive datetime: say which time zone it is in, then use UtcInstant.from_aware()")
        if self.dt.utcoffset() != timedelta(0):
            raise TypeError(f"offset {self.dt.utcoffset()} is not UTC: use UtcInstant.from_aware() to convert")

    @classmethod
    def from_aware(cls, dt):
        if dt.tzinfo is None:
            raise TypeError("naive datetime: refusing to guess its time zone")
        return cls(dt.astimezone(UTC))  # convert (moves the clock), never replace (relabels it)

    def plus(self, minutes):
        return UtcInstant(self.dt + timedelta(minutes=minutes))

    def jd(self):
        return float(_kb.ephem.julian_date(self.dt))

    def iso(self):
        return self.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def local(self, tz):
        return self.dt.astimezone(tz)


def lst_hours(t, lon_deg):
    """Local apparent sidereal time via astronomy L100 #3 (GAST checked against Wallace & Capitaine 2006)."""
    if not isinstance(t, UtcInstant):
        raise TypeError("lst_hours needs a UtcInstant")
    s = _kb.timescales.scales(t.dt)  # JD(UTC) and JD(TT); UT1 ~ UTC (|UT1-UTC| < 0.9 s)
    return (_kb.timescales.gast_hours(s["JD(UTC)"], s["JD(TT)"]) + lon_deg / 15.0) % 24.0
