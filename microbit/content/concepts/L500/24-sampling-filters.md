# Concept: Foundations II — sampling and signal processing

## Why it matters
A micro:bit never sees a signal; it sees samples. Lesson 5 reads light, lesson 6 polls the accelerometer, lesson 8 logs at a fixed rate and lesson 13 runs a sensor task every second. Whether those samples describe the world, and how much a filter can clean them, is decided by two results: the sampling theorem and the arithmetic of averaging. Checks: `labs/L500/24-sampling-filters/foundations2.py`, using synthetic (seeded) traces pushed through the stub's light sensor and accelerometer.

## Definitions
- **Sampling.** $x[n] = x(nT_s)$ with sampling rate $f_s = 1/T_s$. The **Nyquist frequency** is $f_s/2$.
- **Band-limited.** $x(t)$ contains no frequencies above $W$: its Fourier transform $X(f) = 0$ for $|f| > W$.
- **Aliasing.** Two different continuous signals giving identical samples.
- **Moving average (MA, N points).** $y[n] = \frac1N\sum_{k=0}^{N-1} x[n-k]$.
- **Exponential moving average (EMA).** $y[n] = y[n-1] + \alpha(x[n] - y[n-1])$, $0 < \alpha \le 1$.
- **Frequency response.** For input $e^{j\omega n}$ a linear time-invariant filter outputs $H(\omega)e^{j\omega n}$; $\omega = 2\pi f/f_s$.

## Key results
**T1 — sampling theorem (Shannon 1949, Theorem 1).** If $x(t)$ contains no frequencies higher than $W$, it is completely determined by samples spaced $1/(2W)$ apart, and $x(t) = \sum_n x(\tfrac{n}{2W})\,\mathrm{sinc}(2Wt - n)$. *Proof sketch:* on $[-W, W]$ expand $X(f)$ as a Fourier series $X(f) = \sum_n c_n e^{-j\pi n f/W}$. The coefficients are $c_n = \frac{1}{2W}\int_{-W}^{W} X(f)e^{j\pi nf/W}df = \frac{1}{2W}x(\tfrac{n}{2W})$ by the inverse transform. So the samples fix $X$, hence $x$; transforming the series back term by term gives the sinc sum. **Aliasing** is the converse failure: $\cos(2\pi f nT_s) = \cos(2\pi (f - kf_s)nT_s)$ for every integer $k$, so a component at $f$ is indistinguishable from one at $|f - \mathrm{round}(f/f_s)f_s|$. No processing after sampling can separate them; only an analog filter before the sampler (or a faster sampler) can.

**T2 — moving average.** $H(\omega) = \frac1N\sum_{k=0}^{N-1}e^{-j\omega k} = e^{-j\omega(N-1)/2}\frac{\sin(N\omega/2)}{N\sin(\omega/2)}$ (geometric series). DC gain 1; zeros at $f = kf_s/N$, $k = 1..N-1$. If the noise $w[n]$ is independent with variance $\sigma^2$, $\mathrm{Var}(y) = \frac{1}{N^2}\cdot N\sigma^2 = \sigma^2/N$: the standard deviation falls by $\sqrt N$. Correlated noise falls by less.

**T3 — exponential filter.** $H(z) = \frac{\alpha}{1 - (1-\alpha)z^{-1}}$, impulse response $h[n] = \alpha(1-\alpha)^n$. Step response from rest: $y[n] = 1 - (1-\alpha)^{n+1}$. Time constant: $(1-\alpha)^{n} = e^{-1}$ gives $\tau = -T_s/\ln(1-\alpha) \approx T_s/\alpha$ for small $\alpha$. Noise: $\sum h^2 = \alpha^2/(1-(1-\alpha)^2) = \alpha/(2-\alpha)$, so the EMA with $\alpha = 2/(N+1)$ has exactly the noise reduction of an N-point MA, with one multiply and one stored value instead of N.

## Intuition
Sampling is a strobe light: a wheel spinning at just under the strobe rate seems to turn slowly backwards. The MA is a box that smears each sample over N slots; frequencies that complete whole cycles inside the box cancel exactly. The EMA is a leaky bucket: it remembers everything, but older samples leak away geometrically.

## Worked example (numbers from `foundations2.py`)
- A signal band-limited to 4 Hz sampled at 10 Hz is rebuilt half-way between samples with max error 0.0002 by the sinc sum (2,000 samples, middle of the record).
- A lamp flickering at 100 Hz (twice a 50 Hz mains frequency; illustrative, not measured) sampled at 30 Hz gives samples identical to a 10 Hz cosine (to 8e-13). Pushed through the stub's 0–255 light sensor, the FFT peak is at exactly 10.0 Hz — a "10 Hz flicker" that does not exist.
- The 3-point MA at 30 Hz has its first zero at 10 Hz and removes that alias completely (std 70.7 → 0.00) — a happy coincidence of $f_s/N$, not a cure for aliasing in general.
- Stub accelerometer at rest with 40 mg Gaussian noise: a 16-point MA reduces the standard deviation by 3.98 (theory $\sqrt{16} = 4$).
- EMA, $\alpha = 0.2$, $T_s = 0.1$ s: $\tau = 0.448$ s (the approximation $T_s/\alpha$ says 0.5 s), −3 dB at 0.3566 Hz, noise variance ratio 0.1120 measured vs 0.1111 predicted — the same as a 9-point MA.

## Applying it to the board
Choose $f_s$ from the fastest thing you must see, not the fastest the board can go: lesson 13's 20 ms button poll catches a 150 ms tap, while lesson 14's adaptive logger samples at 0.125–10 Hz because temperature changes slowly. Before trusting a periodic pattern in logged data, compute where mains flicker, motor PWM or vibration would alias to at your rate. Filter after sampling to reduce noise; prevent aliasing before sampling or by sampling fast enough.

## Common misconceptions
- *"Nyquist says sample at twice the frequency you care about."* It says twice the highest frequency **present**. Out-of-band energy still aliases into your band.
- *"A digital filter removes aliasing."* After sampling, the alias is a real in-band component.
- *"More averaging is always better."* The MA delays the signal by $(N-1)/2$ samples and blurs steps; the EMA lags by about $\tau$. Lesson 14's detection-delay brief limits how much you may smooth.
- *"$\sqrt N$ always."* Only for independent noise. Drift and slow interference are correlated and average out much less.
- *"The EMA time constant is $T_s/\alpha$."* Close for small $\alpha$ only; at $\alpha = 0.2$ the error is about 10 %.

## Where it is used
Lessons 5 and 6 (sensor reading), 8 (data logging rates), 13 (task periods), 14 (adaptive sampling), 20 (the digital twin's noise model and CUSUM). Validation: synthetic seeded data through the stub; no real sensor data was recorded (validated-stub).
