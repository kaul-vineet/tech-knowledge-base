# 1. Typed UTC instants at every seam

## Status
Accepted (2026-10-30)

## Context
The scheduler works on a local evening (people think "18:50 at the site"), the sky maths needs UTC (Julian Date,
sidereal time), and agent plans arrive as text. The failure lab shows what one relabel costs: the local wall clock
read as UTC moves the sky 330 minutes (5 h 30 min, the IST offset) and the scheduler puts Betelgeuse at -16.4 deg altitude while
its own airmass column still says 1.982. Python's `datetime` lets naive and aware values mix until they meet in
arithmetic, and `replace(tzinfo=...)` relabels without converting.

## Decision
- All sky functions accept only `timeutil.UtcInstant` (frozen; refuses naive and non-zero-offset datetimes).
- Conversion happens in one place, `UtcInstant.from_aware()` (`astimezone`); local time exists only for display.
- Text across a boundary is ISO 8601 with `Z` or an explicit offset; a time without a zone is rejected, never guessed.
- A lint-style test forbids `replace(tzinfo=UTC)` outside the deliberately marked fault line.

## Consequences
- The naive-datetime bug cannot reach sky maths; the relabel bug still type-checks (offset 0 is valid), so the
  independent validator (ADR 0004) and the seam test remain necessary - types narrow the seam, tests close it.
- Slightly more ceremony when writing tests (construct instants explicitly).
