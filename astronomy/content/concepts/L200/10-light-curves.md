**Concept: periods in uneven light curves**

## Why it matters
Variable stars and exoplanets reveal themselves as repeating brightness changes. Ground-based data have daily gaps, clouds and uneven times, so an FFT does not apply and the strongest peak may be an alias rather than the real period.

## Mental model
Try every trial frequency, fit a sine wave at it, and record how much of the variance the sine explains. Peaks mark periods; daily gaps add echo peaks.

```
(t, mag) ──for each f: least-squares sine fit──> power(f) in [0, 1]
peak f ──> P = 1/f ;  echo at |f ± 1 cycle/day| = alias
```

## How it works
1. **Sample like an observer.** 23 clear nights, 48 points each: 1104 points with gaps → see lab step 2.
2. **Compute Lomb–Scargle power.** The time offset τ makes the sine and cosine fits independent; power is the explained fraction of variance → see lab step 3.
3. **Choose a fine grid.** Spacing 1/(10 × baseline) so narrow peaks are not stepped over → see lab step 3.
4. **Recognise aliases and wrong models.** A sine fits a pulsating star; a short box-shaped transit hardly looks like a sine → see lab step 4.
5. **Test significance.** Shuffle the magnitudes, rerun, and count how often noise beats the peak → see lab step 6.

**Worked example (lab run):** the sawtooth variable (P = 0.5671 d) peaks at 0.5669 d with power 0.770; the next peak is at 1.3074 d, the 1-day alias 1/(1/0.5671 − 1) = 1.3100 d. The transit star (P = 3.2127 d) peaks at 0.3211 d with power 0.032, but its magnitudes are skewed (+0.82). Without daily gaps the alias power falls from 0.541 to 0.005.

## Trade-offs
| Method | Use when | Avoid when |
|---|---|---|
| Lomb–Scargle | Smooth, sine-like variability, uneven sampling | Short transits or eclipses |
| Box least squares (BLS) | Transits: flat with short dips | Smooth pulsators |
| Phase dispersion minimisation | Non-sinusoidal shapes | Very few points per cycle |

## Common mistakes
- Reporting the highest peak without checking ±1 cycle/day aliases.
- Treating a small false-alarm probability as proof of the right period: the transit's peak was significant but wrong.
- A grid too coarse for a long baseline.
