"""L500 #26 Ethics: the few numbers an ethics argument about satellite constellations and open data actually needs.

python sky_numbers.py
1. The 7th-magnitude brightness recommendation (COPUOS A/AC.105/C.1/2026/CRP.22/Rev.1, para 9) as a flux ratio.
2. When is a satellite at the zenith still sunlit? (Earth's shadow; why the CRP notes lower orbits spend longer in shadow.)
3. A licence-compatibility check for a derived catalogue (the L400 #21 rule, restated for the case study).
Geometry: spherical Earth (IAU 2015 B3 nominal equatorial radius), cylindrical shadow, no atmosphere. Illustrative only.
"""
import math

R_EARTH_KM = 6378.1
TWILIGHT_ASTRONOMICAL = 18.0  # Sun depression (deg) at the end of astronomical twilight


def flux_ratio(m_bright, m_faint):
    return 10 ** (0.4 * (m_faint - m_bright))


def max_sunlit_depression(h_km):
    """Largest solar depression angle (deg) at which a satellite at the observer's zenith is still sunlit."""
    return math.degrees(math.acos(R_EARTH_KM / (R_EARTH_KM + h_km)))


# Licence terms reduced to the conditions a derived release must keep (L400 #21): BY = credit, NC = non-commercial,
# SA = share-alike. A release licence is compatible when it keeps every input condition; NC + SA together need a person.
TERMS = {"CC-BY-4.0": {"BY"}, "CC-BY-NC-4.0": {"BY", "NC"}, "CC-BY-SA-4.0": {"BY", "SA"},
         "CC-BY-NC-3.0-IGO": {"BY", "NC"}, "CC0-1.0": set()}


def release_ok(inputs, release):
    needed = set().union(*(TERMS[i] for i in inputs))
    if {"NC", "SA"} <= needed:
        return False, "NC and SA inputs cannot both be honoured automatically - needs a person"
    missing = needed - TERMS[release]
    return (not missing), ("keeps every input condition" if not missing else f"drops {sorted(missing)}")


def main():
    print(f"mag 5 vs mag 7 satellite: {flux_ratio(5, 7):.2f}x brighter; mag 4 vs 7: {flux_ratio(4, 7):.2f}x")
    for h in (350, 550, 1200):
        s = max_sunlit_depression(h)
        when = "into astronomical night" if s > TWILIGHT_ASTRONOMICAL else "only in twilight"
        print(f"zenith satellite at {h:>4} km: sunlit until the Sun is {s:.1f} deg below the horizon ({when})")
    for inputs, release in ((["CC-BY-NC-3.0-IGO"], "CC-BY-4.0"), (["CC-BY-NC-3.0-IGO"], "CC-BY-NC-4.0"),
                            (["CC-BY-NC-3.0-IGO", "CC-BY-SA-4.0"], "CC-BY-NC-4.0"), (["CC0-1.0", "CC-BY-4.0"], "CC-BY-4.0")):
        ok, why = release_ok(inputs, release)
        print(f"inputs {inputs} -> release {release}: {'OK' if ok else 'NOT OK'} ({why})")


if __name__ == "__main__":
    main()
