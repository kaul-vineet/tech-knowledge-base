# L600 #05 · Evidence: A robotic-observatory night scheduler

Combines astronomy, simulation and ai-agents. Every number in the lesson, concept note, README, ADRs and question bank is recomputed by `checks_05.py` (exit 0 = OK). Primary sources only. Sources inherited from the astronomy topic were already verified there (astronomy `documentation/VERIFIED-RESOURCES.md`, checked 2026-10-29). I re-used them unchanged and did not re-fetch them.

## Research questions
1. How do you convert a site's local wall clock to the UTC that sky maths needs, without the relabel bug? → Python `datetime` docs.
2. Which airmass formula and sidereal-time route can be checked against a primary source? → Kasten & Young 1989; Wallace & Capitaine 2006; USNO GAST.
3. Which simple weather model has persistence, and who established it? → the two-state Markov chain of Gabriel & Neumann 1962.
4. How do you keep Monte Carlo streams reproducible when runs are added? → NumPy SeedSequence spawning.
5. How do real observatories schedule? → Lampoudi, Saunders & Eastman 2015 (ILP at Las Cumbres); the astroplan scheduling tutorial.

## Sources kept
| Source | URL | Type | Verified here (2026-10-30) | Used for |
|---|---|---|---|---|
| Python docs: `datetime` | https://docs.python.org/3/library/datetime.html | official docs | Fetched. `astimezone(tz)` adjusts the date and time so the result is the same UTC time. `replace(tzinfo=tz)` attaches a zone "without adjustment of date and time data". Whether a naive object means UTC or local time "is purely up to the program". | ADR 0001, failure lab, build task, Q R2 |
| NumPy: Parallel random number generation | https://numpy.org/doc/stable/reference/random/parallel.html | official docs | Fetched (v2.5 manual). `SeedSequence.spawn()` gives independent child streams. With one level of spawning, all states are guaranteed unique. | weather.clear_matrix, FF3, stream-stability test |
| Gabriel & Neumann 1962, *A Markov chain model for daily rainfall occurrence at Tel Aviv*, QJRMS 88(375) 90-95 | https://doi.org/10.1002/qj.49708837511 | paper (primary) | Bibliographic record and abstract read via web search (fatcat/scholar.archive.org metadata and BibSonomy abstract). The paper fits a Markov chain to wet/dry occurrence and accounts for the distributions of dry and wet spells. One secondary listing gives pp. 85-90; the DOI metadata gives 90-95, and I kept 90-95. Full text was not accessed. | ADR 0003, weather.py docstring |
| Lampoudi, Saunders & Eastman 2015, *An Integer Linear Programming Solution to the Telescope Network Scheduling Problem* | https://arxiv.org/abs/1503.07170 | paper (primary) | Abstract fetched. It describes an ILP model derived from the Reservation formalism; the Gurobi-based implementation "can address problems of realistic size". | ADR 0002 alternative, inRealSystems, scaling limit |
| Kasten & Young 1989, Applied Optics 28, 4735 | https://archive.org/download/wikipedia-scholarly-sources-corpus/10.1364%252FAO.1.000024.zip/10.1364%252FAO.28.004735.pdf | paper (primary) | Inherited from astronomy L300 #12. Its test there checks 9 Table II rows to < 0.5 %. Here `airmass(30.0)` = 1.9943 was re-run. | airmass limit, FF1 |
| Wallace & Capitaine 2006, A&A 459, 981 | https://syrte.obspm.fr/iau2006/aa06_459.IAU06prec.pdf | paper (primary) | Inherited from astronomy L100 #3. Re-run here: `gast_hours` vs the published GST of the worked example gives −0.023 s (`test_gast_reproduces_wallace_capitaine_2006`, tolerance 0.1 s). | validator sidereal route |
| USNO: Computing GAST | https://aa.usno.navy.mil/faq/GAST | official | Inherited (astronomy L100 #3 / L300 #12). | both sidereal routes |
| astroplan scheduling tutorial | https://astroplan.readthedocs.io/en/stable/tutorials/scheduling.html | official docs (OSS) | Inherited (astronomy L300 #12). Gives the constraint names used as equivalents. The cross-check run is pendingCi. | inRealSystems, pendingCi |

Dropped: SIMBAD TAP and Sesame queries for extra targets (M31, M42, Rigel and others). web_fetch returned no document for those URLs. Rather than invent coordinates, I used only the 8 SIMBAD stars from astronomy L300 #12 plus Polaris, Canopus and Arcturus from astronomy L100 #2.

## What was verified by running code (Python 3.12.15, numpy 2.5.3, Linux)
- **Night.** There are 64 ten-minute slots of astronomical darkness, 18:50–05:20 IST. The first slot is 2026-11-19T13:20:00Z. 7 of 11 requests are feasible. Fomalhaut stays closer than 30° to the Moon wherever its airmass is ≤ 2. Polaris's airmass stays above 2 all night (altitude ≈ 28.5°). Canopus peaks at 8.84°. Arcturus rises only after slot 40.
- **Plans.** Greedy gives 8.209 (Deneb, Aldebaran, Capella, Betelgeuse). Local search gives 10.534 (Vega, Deneb, Aldebaran, Betelgeuse, Sirius) with hash 4928d62de8143130. Seeds 1, 2, 3 and 2026 give the same plan. Max airmass is 1.939.
- **Weather (1000 runs, seed 7, CRN).** Greedy 8.261 ± 0.272, optimised 10.494 ± 0.306, ratio 1.270, paired difference 2.233 ± 0.190. Greedy wins on 17.8 % of nights. The worst per-block z is 1.68. With a = 0.08: 4.503 vs 5.965 (ratio 1.325), greedy wins 23.0 %.
- **Seams.** The two altitude routes agree to 0.0019°. The fault shifts sky time by exactly 330 min. Under the fault the validator finds Betelgeuse at −16.4° while the scheduler's rows show max airmass 1.982.
- **Agent (fake server only).** The fake plan is rejected for 4 reasons. The +05:30 version of the optimiser's plan is adopted. The explanation passes the number gate.
- **Question bank.** 32 MCQs. 7 calculation answers are recomputed, 5 code-reading snippets are executed, and the answer positions are balanced 8/8/8/8.

## Gaps
- Real local model (Ollama qwen2.5:1.5b) is pendingCi. The astropy/astroplan cross-check is pendingCi. macOS and Windows runs are pendingCi (platforms "expected").
- The weather parameters are assumptions. They are not fitted to Gurgaon cloud records.
- Kasten & Young is applied to true altitude, not apparent (refracted) altitude. This is the same documented limitation as in astronomy L300 #12.
