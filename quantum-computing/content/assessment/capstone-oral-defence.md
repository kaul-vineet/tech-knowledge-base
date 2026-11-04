# Capstone oral defence

**Format:** 15 minutes per student: 3 minutes to present the service (L400 #22) and its scorecard, then about 10 minutes of questions from the bank below, then 2 minutes for the examiner's summary. Each student answers individually, even on a team capstone. Examiners pick 4 questions, at least one from each block (A design, B theory, C evidence and ethics), and ask follow-ups. Students may have their repository open, including `run_capstone.py` output and the ADRs.

## Question bank (10)

### A. Design decisions
1. **Execution mode.** Walk me through ADR 0001 (service execution). Why batched jobs rather than one job per circuit? Which number from `orchestrator.py` (L400 #17) settled it, and what would make you reverse the decision?
2. **Feasibility gate first.** Your service rejects some requests before any quantum work (ADR 0004). Show the decision table. What error budget and code distance does the gate assume, and how would a different physical error rate change the answer (L400 #19)?
3. **Readout-only mitigation.** Why did you not use zero-noise extrapolation in production (ADR 0003)? What did the L300 #13 failure lab show about variance and negative probabilities?

### B. Theory behind the code
4. **Why no exponential speed-up here?** Using T25.1 and the BBBV bound, explain why QAOA on MaxCut should not be *expected* to beat the best classical solver at these sizes. What kind of problem structure *would* change your expectation?
5. **Unitarity and your tests.** Your tests check that probability vectors sum to 1 within a tolerance. Which theorem justifies this for the ideal path, and why do the noisy path's density matrices also have trace 1 (T23.1, T24.4)?
6. **Phase estimation alternative.** If fault-tolerant hardware were available, how would phase estimation (T25.3) change the VQE part of the course? What does the 4/π^2 bound mean for the number of repetitions you need?

### C. Evidence, honesty and responsibility
7. **Code decides the winner.** Show the line where `decide()` picks the solver. How do you stop the local model's explanation from claiming a "quantum advantage" the report does not support (ADR 0002, agent assist)?
8. **Fair benchmark.** What exactly is equal between the quantum and classical solvers (budget, seeds, instances)? If a reviewer found the QAOA win on one 12-node graph, how would you report it honestly (ACM 1.3, IEEE 7.8 item 5)?
9. **If this went to production.** The service handles client data. Which cryptography does it rely on, which of it does Shor's algorithm threaten, and what would your migration plan be (L400 #21, NIST IR 8547)?
10. **Reproducibility.** A teammate on Windows gets a different scorecard. Which parts of the pipeline are seeded or FakeClock-driven, which are not, and how would you find the difference (`PLATFORM-AGENT-SPEC` rules, `platforms` fields)?

## Rubric (per student; 100 points, converted to the 5% weight)

| Criterion | Excellent (90-100%) | Adequate (60-89%) | Inadequate (< 60%) | Weight |
|---|---|---|---|---|
| Technical correctness | Answers are correct and precise. Uses the right theorem or lab number without prompting. | Mostly correct, with minor slips corrected when prompted. | Wrong or vague on core points, or contradicts the repository. | 30 |
| Evidence from own artefacts | Cites ADRs, test names, scorecard lines and real outputs, and can open and run them. | Refers to artefacts in general terms. | Cannot locate or explain own code or ADRs. | 25 |
| Reasoning about trade-offs | Names alternatives, criteria and the reversal condition. Distinguishes measured from assumed. | Gives a reason, but alternatives are thin. | Asserts decisions without reasons. | 20 |
| Professional responsibility | Separates claims from evidence. Raises ethics and security issues unprompted. | Responds well when prompted. | Overclaims, or dismisses the issues. | 15 |
| Communication | Clear, concise, adapts to follow-ups, admits uncertainty precisely. | Understandable, some rambling. | Hard to follow, or evasive. | 10 |

**Integrity check:** if a student cannot explain code they submitted, the examiner records this and the capstone mark for that student is capped at "adequate" pending a follow-up meeting.
