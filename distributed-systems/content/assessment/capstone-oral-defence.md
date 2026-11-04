# Capstone oral defence (week 14) - 20 minutes per team, 5% of the course

Format: 5-minute demo of `python run_capstone.py` (scorecard and one chaos experiment), then 15 minutes of questions. Each team member answers at least two questions alone. Examiners pick 4-5 questions from the bank, at least one theory (T) and one ethics (E) question, and follow up with "how do you know?".

## Question bank (10)
1. **(Design)** Walk us through one ADR in `adr/`. Which alternative did you reject, and which measurement decided it?
2. **(T, consensus)** Your configuration goes through Raft. Which invariant guarantees that two nodes never apply different configs at the same index, and which mechanism maintains it? What happens to it if a node forgets its vote after a restart?
3. **(T, impossibility)** Under which timing conditions can your pipeline fail to make progress, and why can no design rule that out entirely (FLP)? What does your system do meanwhile - is it still safe?
4. **(T, CAP/PACELC)** During a partition between the gateway and the config leader, does your system choose availability or consistency for each operation? Show the code path.
5. **(T, performance)** Your gateway bound is a queue limit. Use Little's law and the M/M/1 delay formula to justify its value from your measured service time and arrival rate.
6. **(T, tail)** Which request in your pipeline fans out, and what is the probability that it hits a slow dependency at your measured per-call p99? What would you change first?
7. **(Verification)** Your scorecard passes on 3 seeds. Why is that evidence, not proof? Which property would you model-check (lesson 21), and with what bounds?
8. **(Failure)** Pick one chaos experiment that failed during development. What was the hypothesis, the blast radius, and the fix? Write the blameless one-line summary.
9. **(E, responsibility)** If this pipeline processed real customers' orders and personal data in the EU, what would change in your failover design and why (GDPR Art. 32, Chapter V)? Who must sign it off?
10. **(E, honesty)** What does your system *not* guarantee? How would you state that limitation to a customer without overselling (ACM 1.3)?

## Rubric (per student, 20 points)
| Criterion | Excellent (5) | Adequate (3) | Inadequate (0-1) |
|---|---|---|---|
| Technical correctness | Answers are right and precise; uses the course's definitions (e.g. linearizable vs eventually consistent) | Mostly right; some imprecision | Wrong or evasive |
| Evidence | Cites own measurements, tests, ADRs or seeds; distinguishes measured from assumed | Some evidence, partly generic | No evidence; "it should work" |
| Theory in practice | Connects the system's behaviour to a theorem from #23-#25 and states the assumptions | Names the theorem but not the assumption | No link |
| Communication and responsibility | Clear, concise, admits limits, handles follow-ups; ethical questions answered with specific principles | Clear but defensive or vague on limits | Unclear or overclaims |

Weighting: the oral mark is the mean of the members' scores, adjusted per member by at most ±2 points for individual answers. Examiners record one sentence of feedback per criterion.
