**Concept: units and magnitudes**

## Why it matters
A catalogue gives a parallax in milliarcseconds and a magnitude; your model needs metres and watts. Two stars of magnitude 6 together are not magnitude 3. Astronomy's units are old, logarithmic and easy to misuse.

## Mental model
Distances use rulers built on each other; brightness uses a reversed logarithmic dial.

```
AU (exact) ──1 arcsec parallax──> parsec (206264.806 AU)      ly = c × Julian year
flux ratio F1/F2 = 10^(−0.4 (m1 − m2))     5 mag = ×100     m − M = 5 log10(d / 10 pc)
```

## How it works
1. **The AU is defined exactly, the parsec follows from it.** 1 AU = 149 597 870 700 m (IAU 2012); 1 pc = 648000/π AU = 3.0857e16 m = 3.2616 ly → see lab step 2.
2. **Magnitudes are logarithms of flux, reversed.** 5 magnitudes are exactly ×100, 1 magnitude ×2.5119, doubling the flux is −0.7526 mag → see lab step 3.
3. **The distance modulus links apparent and absolute magnitude.** A Sun-like star (M = 4.83) is m = 9.83 at 100 pc and m = −26.74 at 1 AU → see lab step 4.

## Common mistakes
- Adding magnitudes instead of fluxes.
- Forgetting the minus sign: brighter means smaller magnitude.
- Inverting a noisy parallax directly; the distance error becomes asymmetric (909–1111 pc for 1.0 ± 0.1 mas).
