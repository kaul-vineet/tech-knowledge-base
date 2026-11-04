**Concept: the astronomy workbench**

## Why it matters
You want to know whether Vega is up tonight, then measure a star in an image. Without a telescope, you need software that gives the same answer on your Mac mini, your Windows PC and in CI, without the internet.

## Mental model
Three layers: a sky simulator to look, numpy code you can read to compute, pinned libraries to cross-check.

```
Stellarium (see) ──> your numpy lab (compute) ──> Astropy/Skyfield in CI (cross-check)
                          │
                labs/data/raw · cache · derived   (offline-first)
```

## How it works
1. **Pin the interpreter and libraries.** Python 3.12 + numpy 2.5.3 run every lab here; Astropy 8.0.2, Skyfield 1.55, SciPy 1.18.1 and photutils 3.1.1 are pinned for the CI equivalents → see lab step 3.
2. **Keep data in three folders.** `raw` is never edited, `cache` is safe to delete, `derived` can be rebuilt from raw. Labs generate seeded synthetic data or use bundled tables, so they run offline → see lab step 4.
3. **Seed every random field.** `default_rng(42)` gives the same synthetic stars (first one at RA 278.6242°, magnitude 8.97) on every run → see lab step 5.

## Common mistakes
- Letting a library download data silently (Astropy IERS tables, Skyfield ephemerides) and then wondering why a lab fails offline.
- Editing files in `raw`: you lose the original.
- Comparing your numbers with a planetarium that applies refraction and precession while your code does not.
