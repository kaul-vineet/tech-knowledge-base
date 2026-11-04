"""Library equivalent (pending-ci): the same night with astropy + astroplan, and a cross-check of ephem.py.

pip install -r ../requirements.txt   (astropy 8.0.2, astroplan 0.10.1 - see KNOWN-GAPS: astroplan's last release is 2024)
python plan_astroplan.py
"""
import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body
from astropy.time import Time
from astroplan import (AirmassConstraint, AtNightConstraint, FixedTarget, MoonSeparationConstraint, ObservingBlock,
                       Observer)
from astroplan.scheduling import Schedule, SequentialScheduler, Transitioner

import ephem
import plan

LOCATION = EarthLocation(lat=plan.SITE["lat"] * u.deg, lon=plan.SITE["lon"] * u.deg, height=217 * u.m)


def astroplan_schedule():
    observer = Observer(location=LOCATION, name=plan.SITE["name"])
    constraints = [AtNightConstraint.twilight_astronomical(), AirmassConstraint(max=plan.MAX_AIRMASS),  # min=1 default
                   MoonSeparationConstraint(min=plan.MIN_MOON_SEP * u.deg)]
    blocks = [ObservingBlock(FixedTarget(SkyCoord(ra * u.deg, dec * u.deg), name=name), plan.BLOCK_MIN * u.min, 0)
              for name, (ra, dec) in plan.TARGETS.items()]
    start = Time(plan.NIGHT)
    schedule = Schedule(start, start + 14 * u.hour)
    SequentialScheduler(constraints=constraints, observer=observer,
                        transitioner=Transitioner(slew_rate=1 * u.deg / u.s), time_resolution=plan.STEP_MIN * u.min)(
        blocks, schedule)
    return schedule.to_table()


def max_differences():
    """Our low-precision Sun/Moon against astropy over the night (degrees)."""
    t = Time(plan.NIGHT) + range(0, 14 * 60 + 1, plan.STEP_MIN) * u.min
    frame = AltAz(obstime=t, location=LOCATION)
    jd = t.utc.jd
    sun_alt, _ = ephem.altaz(*ephem.sun_radec(jd), plan.SITE["lat"], plan.SITE["lon"], jd)
    moon_alt, _, _, _ = ephem.moon_altaz(plan.SITE["lat"], plan.SITE["lon"], jd)
    d_sun = abs(get_body("sun", t, LOCATION).transform_to(frame).alt.deg - sun_alt).max()
    d_moon = abs(get_body("moon", t, LOCATION).transform_to(frame).alt.deg - moon_alt).max()
    return round(float(d_sun), 3), round(float(d_moon), 3)


if __name__ == "__main__":
    print(astroplan_schedule())
    print("max |our - astropy| altitude over the night: Sun %.3f deg, Moon %.3f deg" % max_differences())
