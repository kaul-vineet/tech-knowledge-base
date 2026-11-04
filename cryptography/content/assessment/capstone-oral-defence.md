# Capstone oral defence (week 14) - 20 minutes per team

**Format:** 5-minute demo of the encrypted document service (L400 #22). Then 12 minutes of questions, with every team member answering at least two. Then 3 minutes for the examiners to confer.
**Purpose:** check that each student understands, and can justify with evidence, the design the team built. This is 5 % of the course grade.

## Question bank (examiners pick 5-6 and adapt them to the team's design)
1. **Nonces.** Show where every AEAD nonce in your service comes from. What is your per-key message budget, and how did you calculate it (lesson 24)? What happens after a crash and restart?
2. **Associated data.** Which fields are in the AAD, and what attack succeeds if one is removed? Demonstrate it with the failing test.
3. **Key hierarchy.** Walk through data key → KEK → root. Which keys are non-exportable? What does an attacker who dumps the application's memory get (L400 #19)?
4. **Rotation and revocation.** A user leaves a tenant. Which keys change, which documents are re-encrypted, and how do you know the job finished (metric)?
5. **Post-quantum.** Which parts are quantum-safe today and which are not? Why did you migrate key exchange or wrapping before signatures? What stops a downgrade to classical-only (L400 #18)?
6. **Agility.** Show the registry and the policy. Switch the default AEAD live: what happens to old documents? Run the fitness function (L400 #17).
7. **Security definitions.** Which game (IND-CCA, INT-CTXT, EUF-CMA) does each component need to win, and which library property gives you that (lesson 25)? Name one assumption your design depends on.
8. **Threat model.** Pick one branch of your attack tree and show the test that blocks it. Which threat did you accept, and why (L400 #21)?
9. **Failure evidence.** Show a failure-lab run you reproduced and the fix. How would you detect the same failure in production?
10. **Ethics and disclosure.** A researcher reports a flaw in your sharing feature. Walk through your disclosure policy. Separately, a government asks for access to one tenant's documents: what can you technically provide, and what would you refuse to build (lesson 26)?

## Rubric (per student; the team score is the mean, and individual adjustments are allowed)
| Criterion | Excellent (4) | Adequate (2-3) | Inadequate (0-1) | Weight |
|---|---|---|---|---|
| Technical correctness | Answers are accurate and consistent with the code and lessons | Minor inaccuracies, self-corrected | Wrong or contradicts own code | 30 % |
| Justification with evidence | Cites measured outputs, tests, ADRs or calculations | Justifies from principle only | Assertions only | 25 % |
| Understanding of foundations | Links design to games, budgets and assumptions (L500) | Partial links | None | 20 % |
| Individual contribution and ownership | Can explain the parts others built; knows the trade-offs | Knows own part only | Cannot explain own part | 15 % |
| Communication | Clear, concise, admits uncertainty | Understandable | Unclear | 10 % |

**Integrity:** examiners may ask any student to modify a test or a parameter live. Inability to explain submitted work triggers a follow-up review.
