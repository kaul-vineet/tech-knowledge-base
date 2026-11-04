**Concept: reading a primary paper as an argument**

## Why it matters
Everything in this course rests on papers someone wrote. Docs and tutorials summarise them, sometimes wrongly. Reading the original tells you what was actually claimed, on what evidence, and with which caveats. Engineers need this skill as much as scientists: a data release paper is the specification of the data your pipeline consumes.

## A reading method (four passes)
1. **Claim.** One sentence: what does the paper say is true or available?
2. **Evidence and method.** What data, how many objects, which assumptions, which fit?
3. **Check.** Recompute a few of the paper's own numbers. Run `python reading_checks.py`.
4. **Limits and afterlife.** What did the authors hedge? What did later work change? Be careful not to judge 1929 by 2026 standards.

## Reading 1 - Hubble (1929), PNAS 15, 168
Hubble re-examined the "K term" in solutions for the Sun's motion relative to the nebulae. He used only the 24 nebulae whose distances he trusted:
- the first seven from resolved stars, chiefly Cepheids;
- thirteen from the brightest-star criterion;
- four Virgo-cluster members from mean luminosities.

He introduced distance as a coefficient of K: rK + X cos α cos δ + Y sin α cos δ + Z sin δ = v. He solved twice, for individual nebulae and for nine groups, and adopted K = +500 km/s per million parsecs. He checked the result two ways. The 22 nebulae without individual distances give "K of 530". NGC 7619, at +3910 km/s, lands at 7.8 Mpc with a reasonable absolute magnitude. His final paragraph is cautious: the linear relation is "a first approximation representing a restricted range in distance", and a possible link to de Sitter's cosmology is left for future data.

Checks: 1/K = 1.96 Gyr; 3910/500 = 7.82 Mpc; M = −17.66 versus his −17.65; 745/1.4 = 532. The law survived. The distance scale did not: today's H₀ of about 67–73 km/s/Mpc puts NGC 7619 at about 58 Mpc. That change came from recalibrating the distance indicators (lesson 24), not from the linear form.

*Access and licence.* The paper is free to read on PubMed Central, with a NASA transcription. No open licence was shown on the pages retrieved, so summarise and quote only briefly, with citation.

## Reading 2 - Gaia DR3 summary (Gaia Collaboration, Vallenari et al. 2023, A&A 674, A1)
The paper documents a release built from the first 34 months of Gaia data. Astrometry and broad-band photometry carry over from EDR3. New products include:
- mean radial velocities for more than 33 million objects;
- about 220 million BP/RP and 1 million RVS mean spectra;
- variability analyses for about 10 million sources;
- astrophysical parameters and classification probabilities for hundreds of millions to 1.5 billion sources;
- orbits for about 800,000 binaries;
- more than 150,000 Solar System objects.

For an engineer it is a specification. It tells you what exists, its selection (radial velocities only for G_RVS < 14), and where the validation papers and documentation live.

*Licences.* The article is CC BY 4.0. The data are CC BY-NC 3.0 IGO. These are two licences for two different things (lesson 21).

## Writing the critical response
- Summarise in your own words: claim, method, evidence.
- Separate the authors' evidence, their own hedges, and what came later.
- Include at least two numerical checks and interpret them.
- Cite properly (DOI) and get the licences right.
- Be fair: criticise the argument, not the era.

## Common mistakes
- Treating the paper's abstract as the paper.
- Calling Hubble "wrong" because K was about seven times too large, missing that the linear relation was the discovery.
- Copying long passages instead of summarising.
- Using DR3 data without reading which subsets have which products, then discovering the selection effect after publication.
