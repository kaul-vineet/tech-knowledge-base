# 1. Gate every data release with an automated check (licence, credit, citation, VOTable, manifest)

## Status
Accepted (2026-10-29)

## Context
The lab publishes a small derived catalogue built from three inputs. The rows are synthetic stand-ins; the licences and credit texts are the real ones:
- Gaia DR3 astrometry: "Gaia data are distributed under the CC BY-NC 3.0 IGO license." (ESA Gaia licence page).
- TESS light curves from MAST: most MAST data are public domain, and MAST asks for a mission acknowledgement.
- Our own photometry: we choose CC-BY-4.0.

The release must be FAIR-ish (Wilkinson et al. 2016): readable by VO tools (VOTable 1.5), citable (CITATION.cff 1.2.0, software citation principles), licensed clearly (SPDX id; R1.1 "released with a clear and accessible data usage license"), and its files must be verifiable (SHA-256 manifest). Reviews were manual. The shipped builder licensed everything CC-BY-4.0 and dropped Gaia's NonCommercial condition.

`defects.py` injected 6 realistic defects into a good release; for 5 of them a careful-looking maintainer re-hashed the manifest. Each option was measured on these defects:
- A, a "required files present" review: catches 0/6.
- B, `check()`: manifest hashes, CFF required keys, SPDX id, restriction propagation (NC, SA), verbatim credit lines, VOTable structure (FIELD unit and UCD, TD count, datatype parse): catches 6/6.
- C, B plus external validators (astropy.io.votable `verify="exception"`, `cffconvert --validate`, STILTS votlint) and a DOI deposit: pending-ci or manual. Not measured here.

## Decision
Use B as a blocking CI gate, and run C's validators in CI as a second opinion. `release_licence()` keeps every input restriction (NC, SA). If no standard licence can keep them all (NC + SA conflict), it stops with "needs human review" instead of choosing. The rules are conservative defaults, not legal advice. A person approves every release whose inputs include non-open terms.

## Consequences
- The example release is CC-BY-NC-4.0, which is stricter than our own CC-BY-4.0 parts. Without Gaia it would be CC-BY-4.0 (tryIt 2).
- Credit lines must be verbatim. A paraphrase ("DPAC funding") is rejected, so the acknowledgement text lives in `inputs.py`, quoted once from the provider pages.
- The licence family table (BY, NC, SA, PD) is ours. New input licences (for example ODbL or a custom archive policy) need a new row and a review.
- Our VOTable check covers structure, not the full XML schema. That is why astropy and votlint run in CI.
- Fitness function: `test_fitness.py` requires that check() returns [] for the published release and catches all 6 seeded defects.
