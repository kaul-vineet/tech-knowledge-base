**Concept: CCD calibration - bias, dark, flat and cosmic rays, and how a wrong flat invents variability**

## Why it matters
A camera adds an offset (bias) and thermal signal (dark current) to every pixel, and each pixel has its own sensitivity: vignetting, dust shadows, pixel-to-pixel gain. Remove these imperfectly and the error follows the star across the detector and becomes a signal: a constant star drifting over a dust shadow turns into a "variable star".

## Mental model
Peel the layers the camera added, each measured from frames containing only that layer.

```
raw = bias + dark*t + response x (sky + star) + cosmic rays
 - master bias (zero-second frames)
 - master dark (closed shutter, same t, bias removed)
 / master flat (uniform light, bias removed, normalised to 1)
 = calibrated electrons ~ sky + star     -> clean cosmic rays -> photometry
```

## How it works
1. **Combine robustly.** Each master is a per-pixel combination of 10 frames. A sigma-clipped mean that rejects values beyond 3 robust sigmas (1.4826 × MAD, as in ccdproc) removes cosmic rays from darks → see lab step 2.
2. **Bias and dark.** The master bias here is 999.95 ADU. The master dark is 2.04 ADU (0.05 e⁻/s × 60 s / 1.5 e⁻/ADU), and hot pixels reach 205 ADU → see lab step 2.
3. **Flat field.** Subtract the bias from each flat **before** normalising, because only the light carries the response. Siril: (L − D)/(F − O) → see lab step 5.
4. **Cosmic rays in single frames.** Lights cannot be median-combined while the star moves. L.A.Cosmic's idea is to flag sharp outliers: far above the local median **and** much brighter than their neighbours. A star's PSF spreads light to its neighbours; a cosmic ray does not → see lab step 3.
5. **Photometry and a robust variability test.** Take an aperture sum minus a median annulus sky, then compare the robust rms (1.4826 × MAD) with the photon-noise floor → see lab step 4.

**Worked example (lab run):** without bias subtraction the normalised flat spans 0.8527–1.0792. The truth is 0.821–1.094, so the 1000 ADU pedestal flattens the 25 % vignetting. The constant star's robust rms is 0.899 % against a 0.224 % floor, and it is flagged `variable: true`. Subtracting the bias first gives a flat of 0.813–1.101, an rms of 0.382 % and `variable: false`. Without cosmic cleaning frame 17 jumps to 1.164; the plain rms (2.96 %) would call the star variable, the robust rms (0.377 %) does not.

## Failure modes
- **Wrong or stale flat:** bias left in, wrong filter, moved dust. The "variability" tracks x/y position (log `x` next to `flux_adu`).
- **Brighter flats only hide it:** at 30 000 e⁻ the shipped bug falls under the alarm (0.366 %), but the flat is still wrong.
- **Mean-combined masters:** a cosmic ray in a dark becomes a negative spot in every frame.
- **Over-eager cosmic cleaning:** star peaks get "repaired". Count cleaned pixels per frame (3 here, 4 on frame 17).

## Common mistakes
- Normalising the flat by a mean that bad columns skew; use the median.
- Scaling darks from another exposure or temperature without checking linearity.
- Judging variability with a plain rms that one cosmic ray can dominate.
