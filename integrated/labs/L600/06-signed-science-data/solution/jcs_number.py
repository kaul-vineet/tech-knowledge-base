"""Reference solution (build task): serialise an IEEE 754 double the way ECMAScript Number::toString does, which is
what RFC 8785 (JCS) section 3.2.2.3 requires. Python's repr() already finds the SHORTEST round-trip digits (David Gay,
Python 3.1+); only the layout differs (no '.0', no 'e-07', '1e+21' not '1e21', -0 -> 0)."""
import math


def number(x) -> str:
    if isinstance(x, bool):
        raise TypeError("booleans are literals, not numbers")
    if isinstance(x, int):
        if abs(x) > 2 ** 53:
            raise ValueError("integer outside I-JSON range: send it as a string (RFC 8785 Appendix D)")
        x = float(x)
    if math.isnan(x) or math.isinf(x):
        raise ValueError("NaN/Infinity are not JSON (RFC 8785 3.2.2.3)")
    if x == 0:
        return "0"  # also -0.0
    sign = "-" if x < 0 else ""
    mant, _, exp = repr(abs(x)).partition("e")  # shortest digits, Python layout
    whole, _, frac = mant.partition(".")
    digits = (whole + frac).lstrip("0").rstrip("0")
    if whole == "0":  # 0.00ddd: the point sits before the leading zeros of the fraction (repr adds no exponent here)
        point = -(len(frac) - len(frac.lstrip("0")))
    else:
        point = len(whole) + (int(exp) if exp else 0)
    k, n = len(digits), point  # ECMA-262 Number::toString: s has k digits, value = s x 10^(n-k)
    if k <= n <= 21:
        out = digits + "0" * (n - k)
    elif 0 < n <= 21:
        out = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        out = "0." + "0" * (-n) + digits
    else:
        e = n - 1
        out = (digits if k == 1 else digits[0] + "." + digits[1:]) + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return sign + out
