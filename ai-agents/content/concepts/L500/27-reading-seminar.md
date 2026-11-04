**Concept: reading primary papers – the Transformer and ReAct**

## Why it matters
Everything in this course runs on two ideas that entered the field through two papers: the Transformer (Vaswani et al. 2017), which is the model inside every local and hosted LLM you call, and ReAct (Yao et al. 2023), whose thought–action–observation loop is the agent loop of lesson 6. Reading the originals tells you which claims were measured, under what conditions, and which were hopes. That is the difference between using a technique and being able to judge when it will fail.

## How to read a paper in three passes
1. **Map (15 minutes).** Title, abstract, figures, tables, conclusion. Write down the claim in one sentence and the evidence type (benchmark table, ablation, human study).
2. **Mechanism (60 minutes).** The method section with a pen. Re-derive one equation; for the Transformer, eq. 1 and the √d_k argument you proved in lesson 23. For ReAct, rewrite one trajectory as your lesson-6 loop.
3. **Critique (30 minutes).** For each headline number ask: compared with what, on how many examples, with what variance, and would it survive a different model or task? Note what the authors list as limitations, and what they do not.

## Paper 1 in brief – "Attention Is All You Need"
The paper replaces recurrence with attention in an encoder–decoder translation model. Its core is scaled dot-product attention, softmax(QKᵀ/√d_k)V, run as h = 8 parallel heads of size d_k = 64 inside a d_model = 512 model, plus position-wise feed-forward layers and sinusoidal positional encodings because attention alone ignores order. Section 4 argues for self-attention by per-layer cost (O(n²·d) versus O(n·d²) for recurrence), parallelism (O(1) sequential operations) and path length between distant positions (O(1)). The evidence is BLEU on WMT 2014 English–German and English–French translation, a training-cost comparison, ablations varying heads and key size, and a parsing transfer experiment. The footnote on why dot products grow with d_k is the variance argument from lesson 23.

## Paper 2 in brief – "ReAct: Synergizing Reasoning and Acting in Language Models"
ReAct augments an agent's action space with free-form "thoughts" that do not change the environment but update the context. A frozen model (PaLM-540B) is prompted with a few human-written trajectories that interleave Thought, Action and Observation. On HotpotQA and FEVER the actions are a deliberately weak Wikipedia API (search, lookup, finish). The paper compares Standard, chain-of-thought (CoT), CoT with self-consistency, Act-only and ReAct, then combines ReAct with CoT-SC using simple back-off rules. A human-labelled analysis of 50 trajectories per group contrasts failure modes: CoT hallucinates more, ReAct makes more reasoning errors, including repeating earlier thoughts and actions. On ALFWorld and WebShop, one- or two-shot ReAct beats imitation- and reinforcement-learning baselines. The ethics statement notes the danger of giving a model an action space in real environments.

## Reading for this course
- Connect each paper to code you ran: lesson 23's `attention()` is eq. 1; lesson 6's loop is a ReAct trajectory with a step budget.
- Connect each number to lesson 24: a percentage from 50 labelled trajectories has a wide Wilson interval; a single-run benchmark has no variance estimate.
- Connect the agent paper to lesson 25: ReAct's "repetitive" failure is the stuck loop that a budget bounds, and its actions were safe by construction (read-only APIs) – the allow-list idea.

## Licence and integrity
Both papers are on arXiv and summarised here in our own words; no text, figures or tables are reproduced. Cite them; quote sparingly and with quotation marks; never paste their prose into your response.

## Sources
Vaswani et al. 2017, arXiv:1706.03762v7 · Yao et al. 2023 (ICLR), arXiv:2210.03629v3.
