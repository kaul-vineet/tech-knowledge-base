**Concept: agent-based modelling**

## Why it matters
Planners see neighbourhoods sorting into clusters and ask if strong preferences are needed for that. An agent-based model tests it: give each household a mild rule and watch what the town does.

## Mental model
A flock without a leader: each bird watches only its neighbours, yet the flock turns as one. The pattern lives in the interactions, not in any single rule.

```
for each step:
  every agent: look at 8 neighbours ──> similar share < 30%? ──> move to random empty cell
  measure town: average % similar neighbours
```

## How it works
1. **Agents + local rule:** each agent has a type and a position; it is unhappy if fewer than 30% of its occupied neighbours share its type → see lab step 2.
2. **Interaction drives emergence:** each move changes other agents' neighbourhoods and triggers more moves. Similarity climbs from 50.2% to 75.4% in 17 steps, although nobody asked for more than 30% → see lab step 3.
3. **Same model, framework version:** Mesa supplies the grid, agent set and random activation order (`shuffle_do`); the rule stays the same → see lab step 4.

## Common mistakes
- Reading one run as the answer; setup and order are random, so compare seeds (72.3% to 76.3% for seeds 1 to 5).
- Moving agents in a fixed order, which biases who moves first.
- Treating a toy model as evidence about real people without validation against data.
