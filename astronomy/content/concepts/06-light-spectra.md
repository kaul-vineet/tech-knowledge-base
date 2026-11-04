**Concept: light and spectra**

## Why it matters
A star's colour tells its temperature; a shifted spectral line tells its speed. Pipelines, photometric filters and redshift catalogues all rest on two formulas: Planck's law and the Doppler shift.

## Mental model
A hot object glows with a fixed curve shape that slides to shorter wavelengths as it heats; motion slides every line by the same fraction.

```
T ──Planck B_λ(T)──> spectrum ──argmax──> λ_peak = b / T        ∫ → σT⁴
λ_rest ──motion──> λ_obs      z = λ_obs/λ_rest − 1      v ≈ c z (small z)
```

## How it works
1. **Planck's law gives the curve; Wien's law its peak.** b = 2.897771955e-3 m K; the Sun (5772 K) peaks at 502.0 nm, a 3600 K star at 804.9 nm, numerically and by formula → see lab step 2.
2. **The area under the curve is σT⁴.** Integrating π·B gives 6.2939e7 W/m² for the Sun's surface, the same as σT⁴ → see lab step 3.
3. **Line shifts give velocity.** Hα at 656.50 nm instead of 656.28 nm is +100.5 km/s (receding); at z = 0.1 the simple cz overestimates the relativistic value (29979 vs 28487 km/s) → see lab step 4.

## Common mistakes
- Mixing B_λ (per metre) and B_ν (per hertz): their peaks differ.
- Using v = cz at large z.
- Mixing air and vacuum rest wavelengths.
