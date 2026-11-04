# ADR log – Application Architecture L400

| ADR | Title | Lesson | Status |
|---|---|---|---|
| 0001 | Extract the fines module behind a strangler facade with a parallel run | 17 (`labs/L400/17-strangler-fig/adr/`) | Accepted |
| 0002 | Shared schema with an enforced tenant id; database-per-tenant only as a premium tier | 18 | Accepted |
| 0003 | Authorization rules as an ABAC policy file, evaluated by a decision point, with decision logs | 19 | Accepted |
| 0004 | Schema and API changes use expand/contract, release flags and a guarded contract step | 20 | Accepted |
| 0005 | Run 3 instances (N+1) and send confirmation emails asynchronously; no cache yet | 21 | Accepted |
| 0006 | Keep Library Loans a modular service and extract only the fines module | 22 (this folder) | Accepted |
| 0007 | Every request passes policy, then tenant-scoped SQL, and both are checked in CI | 22 | Accepted |
| 0008 | Loan changes publish events through a transactional outbox; emails are sent asynchronously | 22 | Accepted |
| 0009 | The scorecard decides the release; a local model may only explain it | 22 | Accepted |

Format (Nygard): title, Status, Context, Decision, Consequences. The scorecard criterion "ADR log" checks all nine.
Earlier ADRs: lesson 6 (`labs/L100/06-documenting-architecture/doc/arch/`).
