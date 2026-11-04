**Concept: calibration, identifiability and holdout validation**

## Why it matters
A model is only as good as its parameters, and most parameters are not on a datasheet. Calibration adjusts them until the model matches measured data, here an office cooling down overnight. The trap is that any flexible enough model can match the data it was tuned on. A wrong model can look best exactly when you check it on that same data.

## Mental model
Fitting is the exam you wrote yourself. Validation is a surprise exam on data the model never saw. Only the second tells you whether it can forecast.

```
time ─────────────────────────────►
|■■■■■■■■■■ calibrate (0-8 h) ■■■■■■■■■■|□□□ holdout (8-12 h) □□□|
 fit parameters by least squares           score forecasts here only
```

## How it works
1. **Residuals and least squares.** Choose parameters θ that minimise Σ(model(t; θ) − yᵢ)². For nonlinear models, solve iteratively from starting values (Gauss–Newton or Levenberg–Marquardt) → see lab step 2.
2. **More parameters always fit better in-sample.** RMSE on the calibration data falls from 0.175 to 0.152 to 0.148 °C as the models grow from 3 to 5 to 7 parameters, whether or not the extra parameters mean anything → see lab step 2.
3. **Holdout by time.** For time series, hold out the end, not random points. A random split lets a curve interpolate between neighbours and hides failed extrapolation → see lab steps 3-4.
4. **Identifiability.** If two parameters can trade off and leave the fit unchanged, the data cannot separate them. The covariance s²(JᵀJ)⁻¹ shows this as a correlation near ±1 and large relative standard errors → see lab step 5.
5. **Fix identifiability with information, not cleverness.** Measure one parameter independently (outdoor temperature), log for longer, or simplify the model → see lab step 5.

**Worked example (lab run):** on 0-8 h the degree-6 polynomial has the lowest calibration RMSE, 0.148 °C. On 8-12 h its RMSE is 12.517 °C, and it forecasts −19.60 °C at 12 h, where the sensor read 13.33 °C. The two-exponential physical model scores 0.161 °C on the holdout, close to the 0.15 °C sensor noise. Its parameters are still poorly pinned down: T_inf and the wall time constant correlate at −0.994. Fitted on only 0-5 h, it reports T_inf = −71,014 °C at an RMSE of 0.170 °C.

## Failure modes
- **Same-data validation** picks the most flexible model. You notice the moment a forecast leaves the fitted range.
- **Random holdout on a time series** still prefers poly-6, 0.178 against 0.189 (tryIt 2).
- **Non-identifiable parameters** give a good fit with absurd values. Watch relative standard errors above 50%, correlations near ±1 and starting-value sensitivity.
- **Local minima.** Bad starting values converge elsewhere, so start from physically sensible values.

## Common mistakes
- Quoting fitted parameters as physical facts without standard errors.
- Tuning on the holdout repeatedly until it becomes calibration data. Keep a final, untouched test period.
- Judging by RMSE alone when the residuals show a clear pattern. That pattern means a wrong model structure.
