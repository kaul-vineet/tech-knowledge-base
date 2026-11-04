**Concept: N-body integration**

## Why it matters
Planet systems, star clusters and binary stars have no closed-form solution once three bodies interact. You step them forward in time, and the integrator decides whether your simulated Earth stays in orbit for a century or spirals away in a decade.

## Mental model
Every body pulls on every other; each step nudges velocities by the pulls and positions by the velocities. Leapfrog does this symmetrically, so it never gains or loses energy steadily.

```
Euler:    x += v dt ;  v += a(x_old) dt              (energy drifts)
Leapfrog: v += a dt/2 ;  x += v dt ;  v += a(x) dt/2  (kick-drift-kick, energy oscillates)
```

## How it works
1. **Compute all pairwise accelerations.** a_i = G Σ m_j (r_j − r_i) / |r_j − r_i|³ with G = 4π² in au, years and solar masses → see lab step 1.
2. **Step with Euler or leapfrog.** Same cost per step: one force evaluation → see lab step 2.
3. **Watch a conserved quantity.** Relative energy error |ΔE/E| measures integrator quality without knowing the true answer → see lab step 2.
4. **Check orbits directly.** Earth–Sun distance should stay near 1 au → see lab step 3.
5. **Use the centre-of-mass frame.** If total momentum is not zero, the whole system drifts away → see lab steps 4 and 6.

**Worked example (lab run):** Sun + Earth + Jupiter, 12 years, dt = 0.001 yr. Euler: |ΔE/E| = 1.24e-2 and Earth ends 1.55347 au from the Sun. Leapfrog: 1.22e-12 and 1.00000 au. Reversing time for one year, leapfrog returns Earth to within 1.17e-14 au, Euler misses by 0.585 au. Without the barycentric frame the centre of mass moves 0.0315 au.

## Trade-offs
| Integrator | Use when | Avoid when |
|---|---|---|
| Leapfrog (fixed step) | Long, smooth orbits, energy matters | Close encounters (step too big) |
| Adaptive high order (IAS15) | Close encounters, high accuracy | Millions of steps where speed matters |
| Euler | Teaching only | Any real orbit |

## Common mistakes
- Judging an integrator by one short run.
- Including the self-interaction term (0/0) in the force sum.
- Starting with non-zero total momentum.
