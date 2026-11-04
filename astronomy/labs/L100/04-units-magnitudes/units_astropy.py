"""Astropy 8.0.2 equivalent of units.py (pending-ci). python units_astropy.py"""
import astropy.units as u
from astropy.coordinates import Distance

import units


def compare():
    return [("AU", units.AU, (1 * u.au).to_value(u.m)),
            ("light-year", units.LY, (1 * u.lyr).to_value(u.m)),
            ("parsec", units.PC, (1 * u.pc).to_value(u.m)),
            ("distance modulus 100 pc", units.distance_modulus(100), Distance(100 * u.pc).distmod.value),
            ("flux ratio 5 mag", units.flux_ratio(0, 5), u.Magnitude(-5).physical.value)]


if __name__ == "__main__":
    for row in compare():
        print("%-24s ours %.12g astropy %.12g" % row)
