# Capstone oral defence (week 14)

**Format:** 20 minutes per team: 5-minute demo of the lesson 22 classroom monitor (stub or simulator run, or real boards if available), then 15 minutes of questions to **individual** members. Each member answers at least two questions, one chosen by the examiners from their own role (`team-roles.md`). Examiners may ask for a re-run of a test or the scorecard.

## Question bank (examiners pick 4–6)
1. **Evidence.** Show the scorecard line that proves your gateway rejects a forged frame. What exactly did the test inject, and what would a false pass look like?
2. **Power.** Your boards report every N seconds. Using the lesson 14 model, what battery life do you claim, which input is an assumption, and how would you measure it? (Expect: time-average current over a stated window; the sleep floor is assumed.)
3. **Sampling.** What is your sensor sampling rate, what is the fastest change you must see, and where would 100 Hz lamp flicker alias to? (Lesson 24.)
4. **Real time.** List your tasks with period and budget. Is the set schedulable under rate-monotonic assumptions, and what does your cooperative loop add? (Lesson 25: U, the bound, the blocking term.)
5. **Integrity vs authenticity.** Why do your frames carry both a CRC and a MAC? What does each one catch?
6. **Failure.** Pick one failure your fitness function detects. Show it failing (fault injected) and passing (fault removed).
7. **ADR.** Defend your most contested ADR: the option you rejected, the trade-off you accepted, and the evidence that would make you change your mind.
8. **AI boundary.** Where does the local model appear in your system, and which code path guarantees it cannot change an alarm or a config? (Lesson 21.)
9. **Ethics.** What data leaves the room? Justify each field against the purpose, the retention period and, at policy level, the ICO Children's code or the DPDP Act. (Lesson 26.)
10. **Accessibility.** How would a blind pupil or a pupil with limited fine motor control use your system's outputs and inputs? (Lesson 26.)

## Rubric (per student; 100 points, weighted 5 % of the course)
| Criterion | Excellent (full) | Adequate (about half) | Inadequate (0–20 %) | Weight |
|---|---|---|---|---|
| Technical correctness | Answers are correct and precise; numbers come from the team's own runs | Mostly correct; some numbers recalled rather than shown | Incorrect or evasive | 30 |
| Evidence | Shows tests, scorecard lines or outputs on request; distinguishes stub, simulator and hardware | Refers to evidence without showing it | No evidence; claims beyond what was run | 25 |
| Theory link | Uses L500 results (window-averaged current, aliasing, U and blocking, CRC limits) with assumptions | Names the theory without applying it | No link | 20 |
| Judgement and ethics | States trade-offs, residual risks and data choices with reasons | Lists considerations without a decision | Ignores them | 15 |
| Communication | Clear, concise, answers the question asked | Understandable with prompting | Unclear | 10 |

**Integrity:** a student who cannot explain code they submitted receives at most "adequate" on technical correctness for that part.
