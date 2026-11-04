**Concept: aperture photometry**

## Why it matters
Brightness measurements drive light curves, exoplanet transits and distance estimates. You must separate the star's light from the sky under it and know how precise the number is: a 1% transit is invisible if your error is 5%.

## Mental model
Draw a circle around the star and add up the light; estimate the sky from a ring that holds no star and subtract it. Noise comes from the star, the sky and the detector.

```
     ┌─ annulus r 10–15 px: median sky per pixel
  (  ●  )  aperture r 6 px: sum
net = sum − npix × sky        SNR = net / √(net + npix(1 + npix/nsky)(sky + RN²))
```

## How it works
1. **Weight edge pixels by area.** Sub-sampling each pixel 5 × 5 gives the fraction inside the circle → see lab step 3.
2. **Estimate the sky robustly.** The median of the annulus ignores a few bright pixels from a neighbour → see lab step 2.
3. **Subtract the sky under the aperture.** net = sum − npix × sky → see lab step 3.
4. **Predict the noise with the CCD equation.** Photon noise of star and sky, read noise, plus the uncertainty of the sky estimate → see lab step 4.
5. **Turn flux into magnitude with an error.** σ_m ≈ 1.0857 / SNR → see lab step 6.

**Worked example (lab run):** gain 1 e⁻/ADU, sky 100 e⁻/px, read noise 5 e⁻, PSF σ 1.5 px. The 20,000 e⁻ star measures 20,006.2 e⁻ at SNR 102.6, so σ_m = 0.011 mag. The 1,000 e⁻ star measures 827.5 e⁻ at SNR 6.0: a 17% miss is about one sigma. Radius 3 px gives SNR 11.2 for that faint star instead of 6.0.

## Trade-offs
| Approach | Use when | Avoid when |
|---|---|---|
| Large aperture (≈4σ) | Bright stars, absolute fluxes | Faint stars: sky noise dominates |
| Small aperture + aperture correction | Faint stars, best SNR | PSF changes across the image |
| PSF fitting | Crowded fields | Isolated bright stars (aperture is simpler) |

## Common mistakes
- Using the mean sky when a neighbour sits in the annulus (here: 18,059 instead of 20,000 e⁻).
- Quoting a magnitude without its error.
- Forgetting the gain: ADU are not photons.
