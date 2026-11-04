# Final exam — micro:bit physical computing (week 14)

**Covers:** L100–L500 (all 27 lessons). **Time:** 2 hours. **Total:** 82 marks.
Closed book; one A4 formula sheet; calculator allowed. Show working. Every numeric model answer is recomputed by `research/l500_checks.py` (section "exams").

---

### F1 — Derivation (12 marks)
A small heater is modelled as x[k+1] = 0.95 x[k] + 0.25 u[k] (x = °C above ambient, u = duty in [0, 1], Ts = 1 s).
(a) Find the DC gain K and the range of proportional gains Kp > 0 for which the unsaturated loop is stable. (5)
(b) With Kp = 2 and set-point +3 °C, find the steady-state error. (3)
(c) Explain what integral action changes and one way it can go wrong on the real board. (4)

**Model answer.** (a) K = b/(1 − a) = 0.25/0.05 = **5**; stable iff |0.95 − 0.25 Kp| < 1 → 0 < Kp < 1.95/0.25 = **7.8** (lesson 25, theorem 1). (b) e = r/(1 + K Kp) = 3/11 = **0.273 °C**. (c) At any stable equilibrium the integrator forces e = 0, even with ambient drift; with the duty saturated at 1023 the integrator winds up and overshoots — clamp it or stop integrating while saturated.

### F2 — Proof (12 marks)
CRC-8 with G(x) = x^8 + x^2 + x + 1 (0x07).
(a) Prove that every burst error of length ≤ 8 is detected. (6)
(b) Does it detect every 3-bit error? Prove or disprove. (3)
(c) What fraction of 9-bit bursts at a fixed position escapes? (3)

**Model answer.** (a) Undetected iff G | E; a burst is E = x^i B with deg B ≤ 7, B(0) = 1. G(0) = 1, so gcd(G, x^i) = 1 and G | E ⇔ G | B, impossible because B ≠ 0 and deg B < 8 = deg G. (b) Yes: G(1) = 1 + 1 + 1 + 1 = 0, so (x + 1) | G; a 3-bit error has E(1) = 1, so G ∤ E. (c) L = r + 1 = 9: only B = G escapes, 1 of 2^7 = **1/128 ≈ 0.0078**.

### F3 — Calculation (10 marks)
Three periodic tasks under preemptive rate-monotonic scheduling have (C, T) = (2, 10), (4, 15), (6, 30) ms.
(a) Compute U and the Liu & Layland bound; what do you conclude? (5)
(b) The same tasks run in lesson 13's cooperative loop. Compute the worst response of the 10 ms task if it becomes ready 1 ms after the 6 ms task starts. Does it meet its period? (5)

**Model answer.** (a) U = 0.2 + 0.2667 + 0.2 = **0.6667** ≤ 3(2^{1/3} − 1) = **0.7798**: schedulable under RM. (b) Blocking 6 − 1 = 5 ms plus its own 2 ms = **7 ms** ≤ 10 ms: met (B = 5 ms must be added for a non-preemptive analysis).

### F4 — Short explanation (8 marks)
Why does an ARQ link (lesson 12) need duplicate suppression, and why is "gave_up" not the same as "lost"?

**Model answer.** If an ack is lost the sender retransmits a frame the receiver already delivered; without a sequence check it is delivered twice. The sender gives up when it hears no ack, but the data may have arrived and only the acks been lost — lesson 12's MAX_TRIES = 2 run gave up 4 times while all 20 readings arrived. Check the receiver's gap counter before calling data lost.

### F5 — Design critique (12 marks)
A team's gateway (lesson 17) accepts a config frame if its CRC-16 is valid "so nobody can tamper with it", then pushes it to every board (lesson 18). Critique and fix.

**Model answer.** CRC-16 is linear and keyless: for a desired change E an attacker computes CRC_0(E) and XORs it into the check field (lesson 25, problem 25.8). Use a MAC with a per-fleet key and a sequence number or nonce against replay (lesson 19), verify on the gateway and on each board, keep the CRC only as a cheap noise filter, version and acknowledge config (lesson 18), and never let the local model (lesson 21) decide whether a frame is accepted.

### F6 — Prediction (10 marks)
A board samples a motor's current sensor at 8 Hz; the motor's PWM ripple is 50 Hz.
(a) Where does the ripple appear? (4) (b) Name two remedies and their cost. (6)

**Model answer.** (a) |50 − round(50/8)·8| = |50 − 48| = **2 Hz**. (b) An RC low-pass before the ADC (parts, slower response); sampling above 100 Hz and averaging digitally (CPU, energy, log volume — lesson 14); synchronising the sampler to the PWM (complexity).

### F7 — Ethics (10 marks)
The capstone's data could include per-desk sound levels. Using the ICO Children's code and DPDP Act 2023 s.9 at policy level, propose a minimised design and justify it.

**Model answer.** Purpose: room comfort. Aggregate room-level temperature/light on the gateway every 10 min; compute a room "too loud" flag on the board and do not store sound; no desk or pupil ids; 30-day retention; DPIA before deployment (ICO standards 2 and 8; standard 14 for connected devices; profiling off by default, standard 12). In India, s.9 requires verifiable parental consent for processing children's data and bars tracking or behavioural monitoring of children — a per-desk "engagement score" would be close to that line regardless of consent. Make the dashboard accessible (WCAG 2.2).

### F8 — Reading (8 marks)
Name one assumption of Liu & Layland's model that lesson 13 violates, quantify its effect with lesson 25's result, and say whether the bound is still useful.

**Model answer.** Preemption: lesson 13 is cooperative, so a 20 ms sensor task blocks the 20 ms-period button task — 24 ms response. The bound (U = 0.37 ≤ 0.7798) is still a useful first screen once a blocking term is added; the real brief (catch a 150 ms tap) is met.
