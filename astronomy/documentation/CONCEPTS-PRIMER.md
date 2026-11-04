# Astronomy & Astrophysics — concepts primer (read before lesson 1)

## What applied astronomy computing is for
Modern astronomy is mostly software: telescopes produce files, and code turns them into positions, brightnesses and physical models. Typical uses:
- **Pointing and planning:** where and when is an object up? (Astropy, Skyfield, Stellarium, astroplan)
- **Images to measurements:** FITS files, world coordinates, photometry (astropy.io.fits, photutils, Siril, AstroImageJ)
- **Catalogues and surveys:** cross-matching millions of sources (Astropy, TOPCAT, Gaia archive)
- **Time-domain science:** variable stars, exoplanet transits, alerts (lightkurve, Lomb-Scargle, BLS)
- **Simulation and models:** orbits, N-body dynamics, model comparison (REBOUND, emcee)

## One mental model
Every task is **a measurement in some frame + a model + a check against a trusted reference**.

```
 sky (simulated or archived) ──> data: positions, images, light curves
          │                                   │
   frames: time scale, coordinates,      model: geometry, physics, statistics
   units, pixels ↔ sky                        │
          └──────────────> result ± uncertainty ──> check: published value,
                                                       library equivalent, conserved quantity
```
Most bugs are frame bugs: UTC vs TT, J2000 vs date, 0- vs 1-based pixels, magnitudes vs flux.

## Concept map
| Level | Core concepts | Local agent (code stays the judge) |
|---|---|---|
| **L100** run it | Workbench and offline data; RA/Dec → Alt/Az via sidereal time; UTC/TAI/TT/JD; AU, parsec, magnitudes, distance modulus; Kepler's equation and approximate elements; Planck, Wien, Doppler | Proposes which stars are visible; code computes altitudes and overrules (lesson 2) |
| **L200** build it | Cross-matching on unit vectors with a k-d tree; FITS blocks and TAN WCS; aperture photometry and the CCD equation; Lomb-Scargle, aliases, bootstrap significance; leapfrog N-body and energy conservation | Proposes a class and period; code decides and names the 1-day alias (lesson 10) |
| **L300** harden it | Observation scheduling under constraints; calibration frames (wrong flat → fake variability); plate solving; honest uncertainty (bootstrap, MCMC); reproducible pipelines (stale cache) | Explains schedules or fit results; code validates constraints and numbers (proposal) |
| **L400** design it | Survey pipeline architecture with measured throughput; time-domain alerts and brokers; sky indexing and cone search (HEALPix, TAP); model comparison (rotation curves); open data and citation; capstone transit-search pipeline | Explains alerts and candidates; code classifies and vets (lessons 18, 22) |
| **L500** theory & rigour | Proofs behind the tools: Kepler III, vis-viva, virial theorem, spherical trigonometry; Stefan-Boltzmann, mass-luminosity, the distance ladder; Hubble's law, Friedmann age, Bayes and Metropolis detailed balance; ethics of dark skies, observatory sites and open data; reading primary papers | None in the lessons. Proposal: an agent may explain a proof step or summarise a reading, but code checks every number and the student writes every derivation and response |

## Glossary
| Term | Meaning |
|---|---|
| RA / Dec | Right ascension and declination: coordinates fixed to the sky |
| Alt / Az | Altitude above the horizon and azimuth from north: depend on observer and time |
| sidereal time | Earth's rotation measured against the stars; LST = RA on your meridian |
| JD / TT | Julian Date (running day count); Terrestrial Time (atomic, TAI + 32.184 s) |
| magnitude | −2.5 log10 of flux; brighter = smaller |
| parsec | Distance at which 1 au subtends 1″ (3.2616 ly) |
| FITS / WCS | Astronomy file format / cards that map pixels to sky coordinates |
| aperture photometry | Sum of star light in a circle minus the sky from a ring |
| periodogram | Power versus trial frequency for a time series |
| symplectic integrator | Orbit stepper (leapfrog) whose energy error stays bounded |

## Common misconceptions
1. **"Local time is fine for astronomy."** Astronomical formulas need UTC (or TT/UT1); IST is 5.5 h off and a sidereal day is 23h56m04s.
2. **"Magnitudes add."** Fluxes add; two magnitude-6 stars together are magnitude 5.25, not 3.
3. **"The highest periodogram peak is the period."** Daily gaps create aliases, and a sine model can miss transits even when the peak is "significant".
