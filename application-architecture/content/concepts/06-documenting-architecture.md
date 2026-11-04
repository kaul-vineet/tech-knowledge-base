**Concept: C4 diagrams as text and Architecture Decision Records**

## Why it matters
A newcomer asks: "What talks to what, and why SQLite?" Without the reason, they may blindly keep or
reverse the decision (Nygard). Small text docs in the repo answer both, changed in the same PR
as the code.

## Mental model
A map app: zoom from city view (context) to street view (containers). ADRs are the logbook: one
decision per entry, with reason and cost.

```
Context:    [Member] [Librarian] ─► [Library Loans] ─► [E-mail]
Containers: [Member] ─► [Loans API: Python] ─► [(Loans DB: SQLite)]
ADR 1:      "We will store loans in SQLite behind a repository interface."
```

## How it works
1. **Two zoom levels are enough for most teams.** A C4 container is "an application or a data store"
   that must run, not a Docker container: the SQLite file is one → see lab step 2
2. **Diagrams as text.** Mermaid macros (`Person`, `System_Ext`, `Container`, `Rel(from, to, label,
   techn)`) or a Structurizr DSL model diff like code, and a lint catches a `Rel` to an undefined id
   → see lab step 5
3. **ADRs.** Title, Context, Decision ("We will…"), Status and Consequences, including negative ones.
   Numbers are never reused; a reversed decision is marked superseded, not edited → see lab step 3

## Common mistakes
- Drawing Docker containers or JAR modules as C4 "containers".
- Editing an old ADR to reverse it instead of writing a new one that supersedes it.
- Keeping diagrams only as images, with no reviewable diff.
