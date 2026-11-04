"""BUILD TASK (shipped, unfixed): number formatting for the canonical encoder.
This is what most people write first: Python's repr(). It is shortest-round-trip, so it LOOKS canonical, but its
layout is Python's, not ECMAScript's: 10.0 -> '10.0' (JCS: '10'), 1e-06 -> '1e-06' (JCS: '0.000001'),
-0.0 -> '-0.0' (JCS: '0'). A JavaScript/Go/Java verifier hashes different bytes and every signature check fails.
Fix it so tests/test_build_task.py passes with BUILD_TARGET=mine (RFC 8785 Appendix B samples)."""
import math


def number(x) -> str:
    if isinstance(x, bool):
        raise TypeError("booleans are literals, not numbers")
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        raise ValueError("NaN/Infinity are not JSON (RFC 8785 3.2.2.3)")
    return repr(x)
