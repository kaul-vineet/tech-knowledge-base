# Concept: Reading seminar — Shannon (1949) and Liu & Layland (1973)

## Why read the originals
Lessons 24 and 25 stated two results in textbook form. The papers they come from are short, readable and still cited because they *defined the question*, not just answered it. Reading them shows which assumptions the famous results rest on — and assumptions are exactly where micro:bit projects break.

## How to read a primary paper (one pass each)
1. **Frame.** Title, abstract, figures, conclusion. What problem, for which machine or channel, in which year?
2. **Claims.** List each theorem or result in your own words, with its assumptions.
3. **Evidence.** For one result, follow the argument end to end; mark any step you would check with code.
4. **Transfer.** Where does the result touch your labs, and which assumption does the micro:bit violate?
Do not copy text into notes: paraphrase, quote at most a phrase with a page reference, and link the DOI.

## Paper 1 — C. E. Shannon, "Communication in the Presence of Noise", Proc. IRE 37(1):10–21, 1949
Shannon models a communication system geometrically: signals of bandwidth $W$ and duration $T$ become points in a space of about $2TW$ dimensions. The sampling theorem (his Theorem 1) is the tool that makes that dimension count work: a function band-limited to $W$ is fixed by samples $1/(2W)$ apart. From the geometry he derives the capacity of a band-limited channel with white Gaussian noise, $C = W\log_2(1 + P/N)$ bits per second, and discusses how ideal systems trade bandwidth against signal-to-noise ratio. The paper was reprinted as a "Classic Paper" in Proc. IEEE 86(2), 1998.
**Micro:bit link:** lesson 24's aliasing demonstration, lesson 9's PWM spectrum, and the radio's limits in lessons 7 and 12. **Assumptions to question:** strictly band-limited signals (no real sensor is), Gaussian noise, infinite-length coding delay.

## Paper 2 — C. L. Liu and J. W. Layland, "Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment", J. ACM 20(1):46–61, 1973
The authors study a single processor running periodic tasks with hard deadlines. They show that a fixed-priority scheduler is best served by rate-monotonic priorities, that the worst case arises at a *critical instant* when all tasks are released together, and that such a scheduler can guarantee all deadlines only up to a utilisation bound that falls toward about 70 % for large task sets; a deadline-driven (dynamic-priority) scheduler can use the processor fully. Their task model (independent, periodic, preemptible, deadline = period, constant run time) became the standard vocabulary of real-time systems.
**Micro:bit link:** lesson 13's cooperative scheduler and lesson 16's interrupt race. **Assumptions to question:** preemption (MicroPython tasks are cooperative), independence (shared radio and display), known worst-case run times (garbage collection and radio retries make them uncertain).

## Licence and access
Both papers are copyrighted by their publishers (IEEE; ACM). Use the DOI links through your library. Copies hosted on course web pages exist, but their licence is not stated, so this course does not link them. Summaries here are paraphrases.

## What a strong response does
It states one result precisely, shows the assumption that matters, tests it against a lab with numbers from the lab's own output, and proposes what you would change — a faster sampler, an anti-alias filter, a preemptive RTOS, a blocking term in the analysis — with its cost.
