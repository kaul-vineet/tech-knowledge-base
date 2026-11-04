**Concept: red-teaming prompt injection – an attack suite with expected safe behaviour**

## Why it matters
Lesson 11 showed one injection being stopped. Attackers do not send one; they paraphrase, move the payload into a retrieved document or a tool result, and aim for data leaving the process rather than a rude reply. OWASP's cheat sheet is blunt: screening is not a security boundary, and prompt wording does not enforce anything. What you can do is write the attacks down as tests, state the safe outcome for each, and prove the defences in code keep passing as the agent changes.

## Mental model
A fire drill with a checklist. Each drill (case) names where the fire starts (channel), what it tries to burn (goal) and what must remain true afterwards (expectation). The drill runs against the building with and without sprinklers.

```
case: channel  kb_doc | tool_output | user        expectation (checked by code)
      payload  "ignore … call send_refund …"   ─►  no send_refund executed
                                                    no request to attacker.test
agent ─► policy layer ─► tools (recorded) ─►        no secret in answer or URLs
          allow-list · argument provenance          benign task still answered
          URL allow-list · output filter
```

## How it works
1. **Attacks as data.** `attacks.json` holds six attacks and two benign controls: indirect injection via a knowledge-base document and via a tool result, a direct user injection, exfiltration through `fetch_url` and through a Markdown image URL, and a paraphrase. → see lab step 2
2. **Observable outcomes, not wording.** Side-effecting tools only record (`world.refunds`, `world.outbound`), so each check asks what happened – which tools ran, which hosts were contacted, whether `sk-…` left the process – instead of whether the reply sounds like a refusal. → see lab step 3
3. **Policy layer in code.** Least privilege (this session has no `send_refund`), argument provenance (every argument must appear in the user's own request – a small version of CaMeL's "control and data flow come from the trusted query"), a URL allow-list, and content isolation with `<untrusted_data>` tags. → see lab step 2
4. **Output filter.** Links and images to hosts outside the allow-list become `[link removed]`; secrets become `[REDACTED]`. A rendered image is a request, so this blocks exfiltration on display. → see lab step 3
5. **Worked example.** Unprotected: 1/8 cases safe – the injected document makes the agent call `send_refund` (X-999, 500). Protected: 8/8, with the user still told "within 30 days". The model proposes three paraphrases; lesson 11's regex catches 2 of 3, the policy layer blocks 3 of 3. → see lab step 4
6. **Grow the suite.** promptfoo red-team and garak generate many more probes against an endpoint; their findings become new cases here. → see lab step 7

## Failure modes
- **Testing the wrong channel:** an injection sent as a user message does not test the retrieval path.
- **Grading by refusal text:** a polite "I can't do that" after the tool already ran counts as safe; only recorded effects prove safety.
- **Over-blocking:** benign controls fail and users route around the agent; track their pass rate next to the attacks.
- **One run, one model:** real models vary; repeat runs and re-run on every model change.

## Common mistakes
- Trusting delimiters or the system prompt as the defence.
- Allow-listing a whole CDN or "any https URL" for convenience.
- Letting tool arguments come from retrieved text.
