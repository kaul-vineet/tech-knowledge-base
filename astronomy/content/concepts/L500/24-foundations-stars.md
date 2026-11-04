**Concept: what a star's light tells you, and how far away it is**

## Why it matters
Photometry (lesson 9) gives a flux. Spectra (lesson 6) give a temperature. Light curves (lesson 10) give a period. None of these is a luminosity, a radius, a mass or a distance. The relations that convert one into the other carry most of astrophysics. They also carry most of its uncertainty. This lesson derives those relations and checks them on real calibration numbers and on a seeded synthetic universe.

## Definitions
- **Flux and luminosity.** Flux F is power per unit area at the observer. Luminosity L is the total power emitted. For isotropic emission at distance d, F = L/(4πd²).
- **Blackbody.** A body that absorbs all radiation. It emits the Planck spectrum B_ν(T), the same curve whose peak lesson 6 found with Wien's law.
- **Effective temperature.** Defined by L = 4πR²σT_eff⁴, even for stars that are not perfect blackbodies.
- **HR diagram.** Luminosity against temperature, with temperature increasing to the left. Most stars lie on the **main sequence**, where they burn hydrogen in their cores.
- **Magnitudes.** m = −2.5 log₁₀F + const. Absolute magnitude M is the apparent magnitude at 10 pc. The **distance modulus** is μ = m − M.
- **Distance ladder.** A chain of calibrations. Parallax gives distances to nearby Cepheids. Their period–luminosity relation gives distances to galaxies that host Type Ia supernovae. Those supernovae calibrate distances in the Hubble flow.

## Key results (proved in the lesson's `theorems`)
1. **Stefan–Boltzmann from Planck.** The outward flux πB_ν integrated over frequency equals σT⁴, with σ = 2π⁵k⁴/(15c²h³). The key step is ∫x³/(eˣ−1)dx = 6ζ(4) = π⁴/15, from a geometric series. Then L = 4πR²σT⁴. On a log L – log T diagram, lines of constant radius have slope 4.
2. **Mass–luminosity (homology sketch).** Hydrostatic equilibrium, ideal-gas pressure and radiative diffusion with constant opacity give L ∝ μ⁴M³/κ, and the radius cancels. Real stars follow L ∝ M^α with α of about 3–4 over much of the main sequence. The lifetime is t ∝ M/L ∝ M^(1−α).
3. **The ladder's algebra.** d = 1/p pc; μ = 5 log₁₀(d/10 pc); σ_d/d ≈ 0.461 σ_μ. An error δM in the supernova calibration multiplies H₀ by 10^(δM/5), **whatever the number of Hubble-flow supernovae**.

## Intuition
- T⁴ dominates. A star twice as hot at the same radius is 16 times more luminous. Hot main-sequence stars are therefore very luminous even though they are only modestly larger.
- Massive stars are profligate. L grows like M^3.5 while the fuel grows like M, so a 10 M☉ star lives about 300 times shorter than the Sun. A cluster that still has such stars must be young.
- A ladder is only as strong as its lowest rungs. Averaging many Hubble-flow supernovae beats down their scatter. It cannot remove an error that every one of them shares through the calibration.

## Worked example (real run of `python stars.py`)
- The Planck integral by quadrature is 6.4939394023, equal to π⁴/15. σ from the exact SI constants equals CODATA's 5.670374419 × 10⁻⁸. π∫B_λ dλ at 5772 K equals σT⁴ to 5 digits.
- 4πR☉²σT☉⁴ with the IAU 2015 B3 nominal values gives 3.8280 × 10²⁶ W, the nominal L☉ to 2 × 10⁻⁶.
- A synthetic main sequence (60 stars, L = M^3.5 with 0.05 dex scatter) fits back a slope of 3.481. The effective temperatures follow from L and R: a 20 M☉ star comes out at 23,410 K.
- The Sun's energy budget, 0.007 × 0.1 × M☉c²/L☉, gives **10.36 Gyr**, with M☉ = GM☉/G. With L ∝ M^3.5, a 2 M☉ star lives 1.83 Gyr and a 10 M☉ star 33 Myr.
- Real rung-1 numbers: the Cepheid l Car has an HST parallax of 2.01 mas (Benedict et al. 2007). That gives d = **497.5 pc** and μ = 8.48. After their extinction and Lutz–Kelker–Hanson corrections, M_V ≈ −5.36, matching their −5.35 (problem 24.5).
- Synthetic ladder: 40 parallax Cepheids recover the P–L relation. Eight supernova hosts calibrate M_SN = −19.338 (true −19.3). Sixty supernovae at 0.01 < z < 0.05 give **H₀ = 68.68** (true 70). Calibrating on one host alone gives 67.24. The Monte Carlo spread for σ_μ = 0.10 is 0.0461, matching the analytic (ln 10/5) × 0.10.

## Stellar evolution in one paragraph
A star is born when a contracting gas cloud's core gets hot enough to fuse hydrogen. It then sits on the main sequence for most of its life: about 10 Gyr for the Sun, about 10 Myr for 15 M☉. When the core's hydrogen runs out, the core contracts and shell burning swells the envelope. The star climbs to the red-giant (or, if massive, red-supergiant) region of the HR diagram. Low-mass stars ignite helium, lose their envelopes and end as white dwarfs. Massive stars burn successively heavier elements up to iron, then their cores collapse in a supernova, leaving a neutron star or black hole. Type Ia supernovae are a different channel: a white dwarf in a binary that is destroyed by runaway thermonuclear burning. Their similar peak luminosities, after standardisation, make them the ladder's top rung.

## Common misconceptions
- "Hotter stars are always bigger." No. Radius depends on both L and T. White dwarfs are hot and tiny; red supergiants are cool and huge (problem 24.2: 813 R☉).
- "Magnitude differences are linear in flux." They are logarithmic. Five magnitudes are a factor of 100, and the scale runs backwards: brighter means smaller.
- "1/p is always the right distance." It is the right *formula*. With 10 % parallax errors, inverting a noisy p and selecting stars by p both bias distances. That is the reason for the Lutz–Kelker correction, and a first taste of Bayesian priors (lesson 25).
- "More supernovae fix H₀." They fix the Hubble-flow scatter, not the calibration (theorem 3d).

## Where this is used
- Lesson 4: the distance modulus.
- Lesson 6: blackbody and Wien's law.
- Lesson 9: magnitudes and their errors.
- Lesson 10: periods.
- Lesson 19: Gaia parallaxes.
- Lesson 25: Hubble's law and the H₀ tension.
