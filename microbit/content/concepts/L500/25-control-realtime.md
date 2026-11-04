# Concept: Foundations III — control and real-time theory

## Why it matters
Three earlier designs made silent theoretical bets. Lesson 9 drove PWM outputs open loop. Lesson 13's scheduler gave each task a period and a budget and hoped they fit. Lessons 12 and 15 trusted CRC-16 to catch damaged frames. This lesson proves when each bet pays off and checks it in `labs/L500/25-control-realtime/foundations3.py`.

## Definitions
- **Open loop.** The actuator command is computed from the goal alone ($u = r/K$). **Closed loop.** It is computed from the measured error $e = r - x$.
- **Discrete first-order plant.** $x[k+1] = a\,x[k] + b\,u[k]$, with $a = e^{-T_s/\tau}$ and $b = K(1-a)$ for a process with time constant $\tau$ and DC gain $K$ (here: temperature rise above ambient for heater duty $u \in [0,1]$).
- **Discrete PID (positional form).** $u[k] = K_p e[k] + K_i T_s\sum_{j\le k} e[j] + K_d (e[k] - e[k-1])/T_s$.
- **Periodic task.** $\tau_i = (C_i, T_i)$: worst-case execution time $C_i$, period $T_i$, deadline = end of period. **Utilisation** $U = \sum C_i/T_i$. **Rate-monotonic (RM):** fixed priorities, shorter period = higher priority, preemptive.
- **CRC.** Treat a bit string as a polynomial over GF(2) (coefficients 0/1, addition = XOR). With generator $G(x)$ of degree $r$, the check bits are $R(x) = M(x)x^r \bmod G(x)$; a burst of length $L$ is an error pattern whose first and last flipped bits are $L-1$ positions apart.

## Key results
**T1 — feedback, stability and steady-state error.** Open loop, a plant gain error $K' \ne K$ leaves a steady error $r(1 - K'/K)$ that nothing corrects. With P control $u = K_pe$ the loop is $x[k+1] = (a - bK_p)x[k] + bK_pr$. It is stable iff the pole satisfies $|a - bK_p| < 1$, i.e. $0 < K_p < (1+a)/b$ for $K_p > 0$. At equilibrium $x^* = \frac{bK_p}{1-a+bK_p}r$, so $e^* = \frac{r}{1 + KK_p}$ (using $b/(1-a) = K$): smaller with more gain, never zero, and gain is capped by stability. Add integral action: if the closed loop settles to any equilibrium, the integrator state is constant, so $K_iT_se^* = 0$ and $e^* = 0$ — for any constant disturbance or gain error, provided the loop is stable (check the poles). Derivative action adds damping but multiplies sensor noise by about $\sqrt2 K_d/T_s$, so on noisy micro:bit sensors it usually needs a filter (lesson 24) or is left out.

**T2 — Liu & Layland's RM bound.** $n$ independent periodic preemptible tasks with deadlines equal to periods are schedulable by RM if $U \le n(2^{1/n} - 1)$; the bound falls to $\ln 2 \approx 0.693$ as $n \to \infty$. *Proof sketch:* (i) **critical instant** — a task's longest response occurs when it is released together with all higher-priority tasks (delaying any higher-priority release can only reduce interference), so checking the first job after a synchronous release suffices. (ii) Among task sets that *just* fill the processor, utilisation is smallest when $C_i = T_{i+1} - T_i$ and $C_n = 2T_1 - T_n$. With ratios $r_i = T_{i+1}/T_i$, $U = \sum r_i + 2/\prod r_i - n$; setting the derivatives to zero gives all $r_i = 2^{1/n}$ and $U = n(2^{1/n}-1)$. For $n = 2$: $U(r) = r + 2/r - 2$, minimised at $r = \sqrt2$, $U = 2(\sqrt2 - 1) = 0.8284$. The full proof (including periods more than a factor 2 apart) is Liu & Layland 1973, Theorems 1–5. The bound is **sufficient, not necessary**.

**T3 — CRC detects every burst of length ≤ r.** An error $E(x)$ is undetected iff $G \mid E$ (the CRC is linear: the received remainder changes by $E(x)x^r \bmod G$, and $\gcd(G, x) = 1$ when $G(0) = 1$). A burst of length $L \le r$ is $E = x^iB(x)$ with $\deg B = L-1 < r$ and $B(0) = 1$. Since $G(0) = 1$, $G$ shares no factor with $x^i$, so $G \mid E \Rightarrow G \mid B$, impossible for a non-zero $B$ of lower degree. For $L = r+1$ exactly one pattern ($B = G$) of the $2^{r-1}$ escapes: fraction $2^{-(r-1)}$; for $L > r+1$, $B = G\cdot Q$ with $Q$ monic, $Q(0) = 1$: $2^{L-r-2}$ of $2^{L-2}$, fraction $2^{-r}$. If $(x+1) \mid G$, every odd-weight error is caught, because $E(1) = 1$ but $G(1) = 0$. CRC-16/CCITT-FALSE uses $G = x^{16}+x^{12}+x^5+1$: $G(0) = 1$ and $G(1) = 0$.

## Worked example (numbers from `foundations3.py`)
- Assumed heater: $\tau = 60$ s, $K = 20$ °C at full duty, $T_s = 1$ s → $a = 0.98347$, $b = 0.33057$, P stable for $K_p < 6.000$ (1.1× that diverges, 0.9× settles). Real gain 16 instead of 20, target +5 °C: open loop is 1.000 °C short; P ($K_p = 2$) 0.1515 °C short ($= 5/33$); PI ($K_p = 0.5$, $K_i = 0.02$) ends 0.0000 °C short even after a −2 °C ambient drop; PI pole radii 0.948 and 0.898. The controller writes its duty to the stub's `pin0.write_analog()`.
- RM: bounds 0.8284 / 0.7798 / 0.7568 for $n$ = 2/3/4; 2,985 random task sets under the bound all met their deadlines in exact simulation; the tight set (41,100), (59,141) meets, one more millisecond misses; the harmonic set U = 1 meets while (2,4), (5,10) with U = 1 misses.
- Lesson 13: $U = 5/20 + 20/1000 + 10/100 = 0.37 \le 0.7798$. But lesson 13 is **cooperative** (non-preemptive): a button job released just after the 20 ms sensor task starts waits 19 ms, then runs 5 ms — 24 ms response against a 20 ms period. RM's preemption assumption is violated; the brief (catch a 150 ms tap) still holds, which is why the lesson measures taps, not periods.
- CRC: matches lesson 12's `crc16`, check value 0x29B1; on a 64-bit message every burst up to 16 bits is caught, exactly 1 in 2^15 of 17-bit bursts per position escapes (48 of 48 positions), and all 41,664 three-bit errors are caught.

## Common misconceptions
- *"More gain = less error, so turn it up."* The pole leaves the unit circle at $K_p = (1+a)/b$; with actuator saturation the symptom becomes a limit cycle rather than divergence.
- *"Integral action fixes everything."* Only if the loop stays stable and the actuator is not saturated (integrator wind-up).
- *"U ≤ 1 means schedulable."* For RM it does not; deadline-driven (EDF) scheduling reaches U = 1, shown in the same paper.
- *"The bound applies to my super-loop."* It assumes preemption, independent tasks, no blocking and exact WCETs.
- *"CRC protects against tampering."* CRC is linear and keyless: an attacker can fix it up. Lesson 19 uses a MAC for that reason.

## Where it is used
Lessons 9 (PWM output), 12 and 15 (CRC on frames), 13 (scheduler), 14 (energy-aware timing), 19 (why a MAC, not a CRC), 22 (capstone timing). Validation: stub + numpy only; plant parameters are assumptions (validated-stub).
