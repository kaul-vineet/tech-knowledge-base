**Concept: the expanding Universe, and how to infer its parameters honestly**

## Why it matters
Two ideas from this course meet here. Lesson 6 turned a spectral shift into a velocity. Lesson 15 used a Metropolis sampler to put honest error bars on a transit fit. Cosmology needs both. Redshifts and distances give the expansion rate H₀. H₀ sets the age and density scale of the Universe. And because the best measurements of H₀ currently disagree (the "Hubble tension"), the statistics behind the error bars matter as much as the physics.

## Definitions
- **Scale factor a(t).** Physical distances between distant galaxies scale as a(t), with a = 1 today. The Hubble parameter is H = ȧ/a, and H₀ is its value today.
- **Redshift.** 1 + z = λ_obs/λ_emit = 1/a(t_emit). Light is stretched along with space.
- **Hubble time.** 1/H₀. **Critical density:** ρ_c = 3H₀²/(8πG). **Density parameters:** Ω = ρ/ρ_c.
- **Likelihood.** p(D|θ), the probability of the data given parameters, read as a function of θ. **Prior:** p(θ). **Posterior:** p(θ|D).
- **Markov chain.** A random walk whose next state depends only on the current one, through a transition kernel K(x, y). **Stationary distribution:** π with πK = π. **Detailed balance:** π(x)K(x, y) = π(y)K(y, x).

## Key results (proved in the lesson's `theorems`)
1. **Hubble's law.** If **r** = a(t)**x** for every galaxy, then every observer sees **v** = H**r**. Nobody is at the centre. To first order in z, cz = H₀d. The next term for flat ΛCDM is d_L = (cz/H₀)[1 + (1−q₀)z/2], with q₀ = Ω_m/2 − Ω_Λ.
2. **Friedmann, critical density and age.** A Newtonian expanding sphere gives H² = (8πG/3)ρ − kc²/a². Flatness needs ρ = ρ_c. With matter plus Λ, the age is t₀ = ∫da/(aH) = [2/(3H₀√Ω_Λ)] asinh√(Ω_Λ/Ω_m). It reduces to 2/(3H₀) when Ω_m = 1.
3. **Bayes and Metropolis–Hastings.** Bayes' theorem is the product rule rearranged. The Metropolis–Hastings acceptance min(1, π(y)q(x|y)/(π(x)q(y|x))) makes π(x)K(x, y) symmetric. That is detailed balance, which implies πK = π. Only ratios of π enter, so the evidence p(D) is never needed.
4. **Conjugate posterior for H₀.** Gaussian errors plus a Gaussian prior give a Gaussian posterior whose mean is the precision-weighted average of the data estimate and the prior mean. With a flat prior, the peak is the least-squares slope: maximising the likelihood is minimising χ².

## Intuition
- Raisin bread: every raisin sees every other raisin recede at a speed proportional to distance. Expansion is not an explosion from a point.
- The age is shorter than 1/H₀ if expansion has been slowing (matter) and longer if it has been speeding up (Λ). Today's mixture happens to give an age close to 1/H₀.
- Detailed balance is a local bookkeeping rule. If every pair of states exchanges probability equally in both directions, the overall distribution cannot drift. Designing a sampler pair by pair is far easier than designing it globally.
- A prior is information. When the data are weak, the prior dominates, and that should be reported, not hidden.

## Worked example (real run of `python cosmo_bayes.py`)
- 500 galaxies expand uniformly with H₀ = 67.4. Seen from two different "home" galaxies, v/r is exactly 67.4 and v is parallel to r: no special centre.
- Flat ΛCDM with Planck 2018's Ω_m = 0.315: d_L/(cz/H₀) − 1 = 0.00761 at z = 0.01. The small-z slope is 0.762, against the predicted (1−q₀)/2 = 0.764.
- The Hubble time for 67.4 km/s/Mpc is **14.51 Gyr**. Hubble's own 1929 value of K = 500 gives 1.96 Gyr.
- Critical density: **8.53 × 10⁻²⁷ kg/m³**, or 1.26 × 10¹¹ M☉/Mpc³. Age: **13.7962 Gyr** from three routes that agree (numerical integral, closed form, and an RK4 integration of the Friedmann equation in u = a^(3/2)). Einstein–de Sitter would give 9.67 Gyr.
- Detailed balance on a 5-state target holds to machine precision. A 200,000-step chain's visit frequencies match π to 0.003. A biased proposal *without* the Hastings factor converges to the wrong distribution (total-variation distance 0.175). With the factor, the error is 3 × 10⁻¹⁴.
- 20 synthetic galaxies (σ_v = 300 km/s, true H₀ = 70) give **71.696 ± 2.116** from the closed form, the same from a 40,001-point grid, and 71.69 ± 2.10 from Metropolis. Priors N(67.4, 0.5) and N(73, 1) pull the same data to 67.6 and 72.8.

## The H₀ tension, briefly
Planck 2018 infers H₀ = 67.4 ± 0.5 km/s/Mpc *assuming* base ΛCDM. The SH0ES distance ladder (lesson 24's method) measures about 73 km/s/Mpc, and Riess et al. (2022) report a 5σ difference. Either a systematic error hides in one route, or the model connecting early and late Universe needs revising. Problem 25.10 asks you to evaluate this as an analyst would: identify which assumptions each number depends on before believing either.

## Common misconceptions
- "Galaxies fly apart through space at the speed in Hubble's law." In the expanding-space picture the separation grows because a(t) grows. Redshift measures the stretch, and "recession velocities" beyond c are not a contradiction.
- "cz = H₀d is exact." It is first order in z. At z = 0.05 the correction is already about 4 %.
- "The likelihood is the probability of the parameters." It is not normalised over θ. Only the posterior is a distribution over θ.
- "Metropolis needs the normalising constant." No. Ratios cancel it, which is precisely why MCMC is useful.
- "A flat prior is uninformative." It is flat in the chosen parameter (H₀), not in 1/H₀ or log H₀. The choice should be stated.
- "Detailed balance is required." It is sufficient, not necessary (problem 25.6). Samplers also need irreducibility and aperiodicity to converge.

## Where this is used
- Lesson 6: redshift.
- Lesson 15: MCMC.
- Lesson 18: base rates in alert filtering.
- Lesson 20: model comparison; BIC approximates the evidence that cancels here.
- Lesson 24: the distance ladder that measures H₀.
