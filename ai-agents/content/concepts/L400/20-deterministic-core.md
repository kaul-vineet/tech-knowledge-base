**Concept: deterministic core, LLM at the edge – the model proposes and explains, code decides**

## Why it matters
The LPC1768 guide's capstone had one rule: threshold logic lives in code, and the AI only explains the readings. Agents need the same rule wherever a decision has consequences: refunds, access, severity, money. A model that decides can be talked out of a policy by the very text it is reading (lesson 16). It can approve 120.00 on an 80.00 order, and it will not tell you when it got a rule wrong. Validation helps less than people expect: it catches malformed answers, not well-formed wrong ones. The design goal is that *no* model output can change a decision. Then you prove it with tests.

## Mental model
Draw a boundary. Inside it: facts from systems of record, a pure `decide(facts)` function, and the action. Outside it: everything the model touches. Only typed, validated data crosses the boundary inward, and it may only move the decision in the safe direction.

```
customer text ──► LLM: propose claims ──► schema + allow-list ──► combine(): approve→escalate only
                                                                        ▲
order system ──► facts ──────────────────────► decide(facts) ──────────┘──► decision ──► action
                                                                        │
                                       LLM: explain(decision) ──► check: names this action, no other, no new amounts ──► shown
                                                                  └─ fails / no model ──► template
```

## Design space
- **Model decides.** The policy goes in the prompt. Fast to build, and it handles fuzzy cases, but the decision is as manipulable as the input.
- **Model decides, code validates.** JSON Schema (types, enums, `additionalProperties: false`), an allow-list of actions, and range checks such as "amount ≤ paid". When validation fails, the refusal path sends the case to a person. This stops malformed and out-of-range answers only.
- **Code decides, model at the edge.** The model extracts *claims* from free text (damaged? chargeback threat?) and writes the explanation. Claims are untrusted inputs with a one-way effect (approve → escalate). The explanation is checked against the decision. Beurer-Kellner et al. (2025) present patterns of this kind (action selector, plan-then-execute, context minimisation) as provably resistant to prompt injection. CaMeL (lesson 16) applies the same idea to data flow.

## How to decide
Ask four questions. Can the decision be written as rules over trusted facts? What does a wrong decision cost? Can a person review the hard cases? What must the model contribute that code cannot (reading free text, wording)? If the rules exist, code decides. Use the model where text must be read or written, and make every crossing typed and one-way.

Worked example (12 refund cases, 4 carrying steering text → see lab step 2):

| design | wrong decisions |
|---|---|
| model decides | 6: c02, c04, c05, c06, c08 (120.00 on an 80.00 order), c09 |
| model decides + validation | 5: only c08's out-of-range amount was refused |
| code decides, model at edge | 0 |

The fitness test feeds 600 seeded hostile answers into the edge (12 cases × 50 seeds). The answers include wrong types, unknown actions, extra keys, 5,000-character strings, invalid JSON and contradicting explanations. Result: 0 changed decisions. The only allowed move is approve_auto → escalate on a threat claim (c09). The shipped explanation check is the build task. Before it, c04's customer reads "Good news: your refund of 40 is approved." while code denied the refund. After it, they read the policy template.

## Failure modes at scale
- **Trusted-by-accident inputs:** a fact the model extracted ends up in `decide()`. Watch the decision function's signature and data lineage; only system-of-record fields go in.
- **Explanation drift:** the decision is right but the text says otherwise. Watch the template fallback rate; a sudden rise means the model or prompt changed.
- **Policy pressure:** people want the model to "just handle" edge cases. Watch the escalation rate; when it grows, add rules (with tests), not autonomy.

## Common mistakes
- Treating schema validation as a safety boundary; it only checks shape.
- Letting the model's suggested action pre-fill the UI that a person approves (anchoring).
- No refusal path: when the model is down, the decision must still happen, with a template message.
