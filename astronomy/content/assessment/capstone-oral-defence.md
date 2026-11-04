# Capstone oral defence — exoplanet transit search pipeline (lesson 22)

**Format:** 20 minutes per student or team member.
- 5 minutes: the student presents the pipeline and its scorecard.
- 12 minutes: questions from two examiners, who draw at least 4 from the bank below and follow up.
- 3 minutes: the student's own critique of the design.

Every team member must be able to answer for every part of the system (see `team-roles.md`).
**Weight:** 7 % of the course (syllabus).

## Question bank (examiners pick at least 4; each probes a different area)
1. **Physics.** Derive the transit-duration bound your pipeline uses (T ≈ 13 h × (P/yr)^(1/3) for a Sun-like star). Which assumptions does it make, and how does your search window (1.5 × the bound) protect you when they fail?
2. **Statistics.** Your scorecard reports 3/3 planets and 0/9 false positives. What is the uncertainty on a 0/9 false-positive rate? Is that sample large enough to claim the vetter "works"? Name one quantity you would measure with injections.
3. **Uncertainty.** The depths are "within 3σ". Where do your σ values come from, how did you check that they are honest (coverage, χ²_red), and what would red noise do to them?
4. **Bayesian reasoning.** Suppose the prior rate of real planets among BLS peaks is 1 %. Your vetter passes 90 % of real planets and 5 % of false alarms. What fraction of passed candidates are real (0.1538), and what does that imply for follow-up planning?
5. **Architecture.** Walk through ADR 0001 and ADR 0002. Which alternative did you reject, on what evidence, and what fitness test would fail if a future change re-introduced the rejected option?
6. **Reproducibility.** Show how a reviewer reproduces your scorecard byte-for-byte from a clean checkout. What is hashed, what is pinned, and what is still platform-dependent?
7. **Failure analysis.** Name the most likely way your pipeline produces a false planet: odd/even depth differences, a secondary eclipse, or an alias of the window function. Show the test that catches it.
8. **Local agent.** Where does the local model appear in your pipeline? Prove that it cannot change a decision, and that its explanations are checked. What happens when the model server is down?
9. **Data and licences.** If you ran on real TESS or Gaia data, what acknowledgement and licence would your released candidate list need? Why can Gaia-derived columns not be released CC BY 4.0?
10. **Ethics and communication.** A journalist asks whether you "found three new Earths". Give the accurate one-minute answer, including what the pipeline can and cannot establish (radius versus mass, false-positive probability, need for follow-up).

## Rubric (per student; total 100, scaled to 7 %)
| Criterion | Weight | Excellent (90–100 %) | Adequate (60–75 %) | Inadequate (< 50 %) |
|---|---|---|---|---|
| Technical correctness | 30 | Derivations and numbers right first time; links code to physics precisely | Minor slips, self-corrected | Errors in core physics or statistics |
| Evidence and verification | 25 | Every claim backed by a test, measurement or recorded run; knows the limits of each check | Most claims backed; some limits unclear | Claims without evidence; cannot locate the test |
| Design reasoning | 20 | Explains trade-offs, rejected alternatives and how the fitness tests guard decisions | Describes the design but not the alternatives | Cannot justify choices |
| Ownership of the whole system | 15 | Answers confidently on parts built by teammates | Hesitant outside own component | Cannot explain teammates' components |
| Communication and honesty | 10 | Clear, concise, states uncertainty and limitations unprompted | Clear but overstates certainty once | Overclaims or evades |

**Moderation.** Two examiners mark independently. If they differ by more than 15 points, a third examiner marks from the recording. Students may request a recording of their own defence.
