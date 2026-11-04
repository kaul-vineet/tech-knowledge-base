"""Astropy 8.0.2 equivalent of light.py (pending-ci). python light_astropy.py"""
import astropy.units as u
from astropy import constants as const
from astropy.modeling.models import BlackBody

import light


def compare():
    bb = BlackBody(temperature=5772 * u.K)  # returns B_nu per steradian by default
    lam = 500 * u.nm
    b_lambda = bb(lam).to(u.W / u.m**2 / u.m / u.sr, equivalencies=u.spectral_density(lam))
    ratio = b_lambda.value / float(light.planck(500e-9, 5772))
    # Wien constant from CODATA constants: b = h c / (k x), x = 4.965114231744276 (root of x = 5(1 - e^-x))
    b = (const.h * const.c / (const.k_B * 4.965114231744276)).to_value(u.m * u.K)
    return ratio, b


if __name__ == "__main__":
    r, b = compare()
    print(f"astropy / light.py B_lambda(500 nm, 5772 K) = {r:.9f}; Wien b = {b:.9e} m K")
