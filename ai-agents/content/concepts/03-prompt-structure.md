**Concept: roles, examples and delimiters shape the token sequence**

## Why it matters
You classify 10,000 reviews. With one big user message the model replies "Sure! Reading the review carefully…" and your parser breaks on every row. Putting rules, examples and data in the right places gives a clean label most of the time.

## Mental model
A function definition: the **system** message is the body (rules), the **user** message is the argument (data), and **few-shot** pairs are worked examples the model imitates. The server flattens it into one script.

```
system: rules            <|im_start|>system rules<|im_end|>
user: example     ───►   <|im_start|>user ...<|im_end|>
assistant: LABEL          ...
user: <review>data</review>   <|im_start|>assistant ← model continues
```

## How it works
1. **Roles separate rules from data.** System messages carry directives and usually come first; user messages carry inputs. Layout A (user-only) returns a **23-word** sentence; layout B returns `negative`. → see lab step 2
2. **The chat template** turns the list into one token sequence with control tokens. Each model family has its own template, so let the server apply it. A two-message example renders to **195 characters** (ChatML-style, illustrative; `research/concept_examples.py`). → see lab step 2
3. **Few-shot examples and delimiters** fix the format and fence the data: layout C copies the examples' casing and returns `NEGATIVE`. → see lab step 2

## Common mistakes
- Rules and data in one user message, then "ONLY reply…" in capitals.
- Examples that contradict the instructions (lowercase rule, uppercase examples).
- Believing delimiters stop prompt injection – they reduce confusion, not permissions.
