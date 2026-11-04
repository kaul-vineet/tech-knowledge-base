**Concept: Modularity theory – information hiding, dependency graphs, layering and Martin's metrics**

## Why it matters
Every boundary in this course – the layers of lesson 2, the module rule of lesson 3, the ports of lesson 7, the strangler
facade of lesson 17 – rests on one idea and one data structure. The idea is Parnas's information hiding (1972). The data
structure is the dependency graph. With the graph you can *prove* things about a code base instead of arguing about them:
that a layering rule rules out cycles, that a cycle makes several modules behave as one, and how far a module is from the
balance Martin's metrics describe.

## Definitions
- **Module (Parnas).** A responsibility assignment, not a subroutine. Each module hides one design decision that is hard or
  likely to change, behind an interface that reveals as little as possible about it.
- **Dependency graph.** G = (V, E), V the modules, u → v if u imports or calls v. "Must I change u when v changes?" becomes
  "is there a path from u to v?"
- **Cycle, SCC, condensation.** A cycle is a path that returns to its start. A strongly connected component (SCC) is a
  maximal set of mutually reachable modules. The condensation G* has one node per SCC.
- **Strict layering.** A function ℓ: V → ℕ with ℓ(u) > ℓ(v) for every edge u → v ("only depend downwards, never sideways").
- **Martin's metrics (1994).** Ca = afferent couplings (who depends on me), Ce = efferent couplings (whom I depend on),
  instability I = Ce/(Ca + Ce), abstractness A = abstract classes / all classes, normalised distance Dn = |A + I − 1|.

## Key results (proofs in `content/L500.json`, checks in `labs/L500/23-modularity-theory`)
1. **T23.1 Strict layering ⇔ acyclic.** If every edge goes to a strictly lower layer, a cycle would give ℓ(v₀) > ℓ(v₀).
   Conversely, in a finite acyclic graph the longest-path length ℓ(v) is a strict layering. The word *strict* is essential:
   two modules in the same layer may import each other.
2. **T23.2 The condensation is acyclic.** Any cycle lives inside one SCC. Modules in a non-trivial SCC must be understood,
   tested and released together – for change they are one module, whatever the folder names say.
3. **T23.3 The main sequence.** I and A lie in [0, 1]; the distance from (I, A) to the line A + I = 1 is |A + I − 1|/√2.
   Martin argued that stable components should be abstract (so they can be extended without modification) and unstable
   ones concrete. The corners (0, 0) – stable and concrete, the "zone of pain" – and (1, 1) – abstract and unused – are the
   worst places to be.

## Intuition
Information hiding is about *where change lands*. Parnas compared two decompositions of a small KWIC index program. The
conventional one splits by processing step (input, circular shift, alphabetise, output), so the decision "how lines are
stored" is known by almost every module. The unconventional one gives that decision to one module (line storage) and
lets the others use it through functions. In our model of the paper (`modularity.KWIC_*`), five plausible design changes
cost 14 module changes in the first decomposition and 5 in the second. The graph view explains why: change propagates
backwards along edges, and a hidden decision has only one module that knows it.

Layering is a cheap global guarantee. Checking "every import goes to a lower layer" is local (look at one edge at a time),
yet T23.1 turns it into a global property (no cycle anywhere). That is why architecture fitness functions such as
import-linter contracts or the lesson 3 boundary check are so effective for their cost.

## Worked example: the real Library Loans code
`check_modularity.py` reads the L200 #7 hexagonal lab with `ast` and finds 10 import edges and a strict layering:
ports (0) ← domain (1) ← four adapters (2) ← app (3). Martin's metrics:

| module | Ca | Ce | I | A | Dn |
|---|---|---|---|---|---|
| ports | 1 | 0 | 0.000 | 1.00 | 0.000 |
| domain | 5 | 1 | 0.167 | 0.00 | 0.833 |
| adapters (each) | 1 | 1 | 0.500 | 0.00 | 0.500 |
| app | 0 | 5 | 1.000 | 0.00 | 0.000 |

The ports sit exactly on the main sequence at the "stable and abstract" end, and app at the "unstable and concrete" end –
as the hexagonal style intends. The domain is furthest away: everything depends on it and it is fully concrete. Is that
bad? Partly. Driving adapters import the domain only for its exception classes, so a change to those exceptions ripples
outwards. Problem P23-4 tries moving them into ports and shows the average Dn gets *worse* (0.405 → 0.488): ports becomes
stable *and* concrete. The metric is a prompt for a conversation, not a verdict.

The analysis also found something the earlier labs never flagged. Read with its `if __name__ == "__main__":` blocks, the
graph has the SCC {app, driving_cli}: the CLI's entry block imports the composition root, which imports the CLI. At import
time there is no cycle, so the tests pass; in the source text there is one, and the CLI cannot be reused without app.
Problem P23-6 asks you to argue whether that is architectural and to propose a fitness function.

## What the evidence says (briefly – lesson 25 goes deeper)
Dependency structure does carry signal. Zimmermann and Nagappan (2008) applied network analysis to the dependency graph of
Windows Server 2003 and predicted defect-prone binaries with recall about 10 percentage points higher than complexity
metrics. But metric "validations" are fragile: El Emam et al. (2001) found that once class size was controlled for, the
object-oriented metrics they studied were no longer associated with fault-proneness. Martin himself closed his paper by
warning against making every design conform unconditionally to his metrics. Use them to find hot spots and to ratchet
(no new cycles, no new edges into unstable modules), not as a quality score.

## Common misconceptions
- **"Folders are modules."** A module is a hidden decision. Two folders in one SCC are one module for change purposes.
- **"Layered means acyclic."** Only *strict* layering does; same-layer imports can close a cycle (1659 of 2000 random graphs
  in the lab).
- **"Low Dn means good design."** Dn measures conformance to one pattern. A module can sit on the main sequence and still
  leak its secrets through its interface.
- **"Stable means unchanging."** Martin's stability means *hard to change* (many dependents), which is exactly why stable
  code should be abstract.
- **"A cycle that only exists in `__main__` is harmless."** It does not break imports, but it couples an adapter to the
  composition root and will confuse every tool and reader that sees the source.
- **"Information hiding is encapsulation of fields."** Private fields help, but Parnas's criterion is about *which design
  decisions* a module owns; a class with private fields whose interface exposes its storage format hides nothing.

## Check yourself
1. Why does T23.1's proof fail if same-layer edges are allowed? 2. What does a non-trivial SCC mean for release planning?
3. Which Library Loans module is in the "zone of pain" corner, and what would you do about it?
