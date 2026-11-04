# ADR 0009: The scorecard decides the release; a local model may only explain it

## Status

Accepted (2026-10-28).

## Context

A release touches strangler cut-over, tenancy, policy, events, SLOs, contracts and capacity. Reviewers want
one answer ("can we ship?") and a short explanation. Language models write fluent summaries but can state
a GO that the evidence does not support; the agent-assist exercises in lessons 15 and 21 rejected drafts with wrong numbers.

## Decision

1. `run_capstone.py` computes every criterion from running code and prints one JSON line per criterion plus a
   summary; the verdict is GO only if every criterion passes (exit code 0), else NO-GO (exit code 1).
2. `agent_assist.py` may draft a go/no-go note from the summary. Code rejects a note whose verdict word or
   numbers differ from the scorecard; nothing is sent automatically, and no secrets or member data go into the prompt.
3. CI runs the capstone without faults (must be GO) and with each seeded fault (must be NO-GO).

## Consequences

- The release rule is reviewable code; changing a threshold is a code change with history.
- Seeded-fault runs keep the gates honest: a gate that never fails is noticed.
- The model is optional; the release process works without it.
