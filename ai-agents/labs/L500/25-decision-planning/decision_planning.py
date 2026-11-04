"""Lesson 25 - decision theory and planning for agents (Python standard library only).

Expected utility, the expected cost of retries and why loops need budgets, a small MDP solved by
value iteration, BFS / A* search, and why "does this tool program ever call delete?" cannot be
decided in general (so agents use allow-lists).

    python decision_planning.py            demo
    python decision_planning.py check T1   numerical check of theorem T1 (T1..T4)
"""
import heapq
import random
import sys
from collections import deque


# ---------------------------------------------------------------- expected utility and retries
def expected_utility(outcomes):
    """outcomes: list of (probability, utility). Probabilities must sum to 1."""
    assert abs(sum(p for p, _ in outcomes) - 1) < 1e-9
    return sum(p * u for p, u in outcomes)


def expected_attempts(p, k):
    """E[min(N, k)] for N ~ Geometric(p): attempts used when each try succeeds with prob p, budget k."""
    return k if p == 0 else (1 - (1 - p) ** k) / p


def expected_retry_cost(p, k, c_call, c_fail):
    """Cost of the calls actually made plus the cost of giving up after k failures."""
    return c_call * expected_attempts(p, k) + c_fail * (1 - p) ** k


def retry_cost_seq(ps, c_call, c_fail):
    """Expected cost when attempt i succeeds with conditional probability ps[i] (given all earlier failed)."""
    cost, p_reach = 0.0, 1.0
    for p in ps:
        cost += p_reach * c_call
        p_reach *= 1 - p
    return cost + p_reach * c_fail


def best_budget(ps, c_call, c_fail):
    """Budget k (1..len(ps)) with the lowest expected cost; ties -> smaller k."""
    return min(range(1, len(ps) + 1), key=lambda k: (round(retry_cost_seq(ps[:k], c_call, c_fail), 12), k))


def simulate_attempts(p, k, runs, seed):
    rnd = random.Random(seed)
    total = fails = 0
    for _ in range(runs):
        for attempt in range(1, k + 1):
            if rnd.random() < p:
                total += attempt
                break
        else:
            total += k
            fails += 1
    return total / runs, fails / runs


# ---------------------------------------------------------------- MDP and value iteration
# One support ticket. In 'open' the agent may: auto (call the refund tool), escalate (a person handles it), close (give up).
# auto: resolved (+10), tool error -> still open (0.20), wrong refund (-50); each auto step costs 1.
def make_mdp(p_harm=0.05):
    return {
        "open": {
            "auto": [(0.80 - p_harm, "resolved", 10 - 1), (0.20, "open", -1), (p_harm, "harm", -50 - 1)],
            "escalate": [(1.0, "handed_off", 4)],
            "close": [(1.0, "closed", -5)],
        },
        "resolved": {}, "harm": {}, "handed_off": {}, "closed": {},  # terminal
    }


MDP = make_mdp(0.05)


def bellman(V, mdp, gamma):
    newV, policy = {}, {}
    for s, acts in mdp.items():
        if not acts:
            newV[s] = 0.0
            continue
        q = {a: sum(p * (r + gamma * V[s2]) for p, s2, r in outs) for a, outs in acts.items()}
        policy[s] = max(q, key=q.get)
        newV[s] = q[policy[s]]
    return newV, policy


def value_iteration(mdp, gamma=0.95, tol=1e-10):
    V = {s: 0.0 for s in mdp}
    for it in range(1, 10000):
        newV, policy = bellman(V, mdp, gamma)
        if max(abs(newV[s] - V[s]) for s in mdp) < tol:
            return newV, policy, it
        V = newV
    raise RuntimeError("no convergence")


# ---------------------------------------------------------------- search
GRID = ["S....#....",
        ".....#....",
        ".....#....",
        ".....#....",
        "..........",
        ".....#....",
        ".....#...G"]


def neighbours(grid, cell):
    r, c = cell
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < len(grid) and 0 <= cc < len(grid[0]) and grid[rr][cc] != "#":
            yield (rr, cc)


def find(grid, ch):
    return next((r, c) for r, row in enumerate(grid) for c, x in enumerate(row) if x == ch)


def bfs(grid):
    start, goal = find(grid, "S"), find(grid, "G")
    dist, q, expanded = {start: 0}, deque([start]), 0
    while q:
        cell = q.popleft()
        expanded += 1
        if cell == goal:
            return dist[cell], expanded
        for n in neighbours(grid, cell):
            if n not in dist:
                dist[n] = dist[cell] + 1
                q.append(n)
    return None, expanded


def astar(start, goal, succ, h):
    """succ(node) -> [(neighbour, cost)]; h(node) -> heuristic. Returns (cost, path, expanded)."""
    frontier, g, parent, closed, tie = [(h(start), 0, 0, start)], {start: 0}, {start: None}, set(), 0
    while frontier:
        *_, node = heapq.heappop(frontier)
        if node in closed:
            continue
        closed.add(node)
        if node == goal:
            path = [node]
            while parent[path[-1]] is not None:
                path.append(parent[path[-1]])
            return g[node], path[::-1], len(closed)
        for n, cost in succ(node):
            if n not in g or g[node] + cost < g[n]:
                g[n], parent[n] = g[node] + cost, node
                tie += 1
                heapq.heappush(frontier, (g[n] + h(n), -g[n], tie, n))  # ties: deeper node first
    return None, None, len(closed)


def grid_astar(grid, weight=1.0):
    start, goal = find(grid, "S"), find(grid, "G")
    h = lambda n: weight * (abs(n[0] - goal[0]) + abs(n[1] - goal[1]))  # Manhattan: admissible when weight <= 1
    return astar(start, goal, lambda n: [(m, 1) for m in neighbours(grid, n)], h)


# A plan graph: steps an agent could take to answer "refund order 42"; edge costs = expected seconds.
PLAN = {"start": [("lookup_order", 1), ("search_kb", 2)],
        "lookup_order": [("check_policy", 6)],
        "search_kb": [("check_policy", 1)],
        "check_policy": [("draft_reply", 1)],
        "draft_reply": []}
H_ADMISSIBLE = {"start": 3, "lookup_order": 7, "search_kb": 2, "check_policy": 1, "draft_reply": 0}
H_OVERESTIMATE = {"start": 3, "lookup_order": 1, "search_kb": 9, "check_policy": 1, "draft_reply": 0}


# ---------------------------------------------------------------- undecidability -> allow-lists
def collatz_then_delete(n):
    """A 'tool program': loops while n != 1 (Collatz), then calls delete. Whether it ever deletes
    depends on whether the loop halts - for arbitrary programs that is the halting problem."""
    def program():
        x = n
        while x != 1:
            x = 3 * x + 1 if x % 2 else x // 2
            yield ("step", None)
        yield ("call", "delete_records")
    program.declared_tools = {"delete_records"}
    return program


def never_deletes():
    def program():
        if False:
            yield ("call", "delete_records")  # unreachable, but present in the program text
        yield ("call", "read_ticket")
    program.declared_tools = {"read_ticket", "delete_records"}
    return program


def dynamic_check(program, budget):
    """Run the program for at most `budget` steps: 'calls delete', 'no delete', or 'unknown'."""
    for i, (kind, tool) in enumerate(program()):
        if i >= budget:
            return "unknown (budget exhausted)"
        if kind == "call" and tool.startswith("delete"):
            return "calls delete"
    return "no delete"


def allow_list_check(program, allowed=frozenset({"read_ticket", "lookup_order", "draft_reply"})):
    """Decidable, sound, conservative: reject any program that can name a tool outside the allow-list."""
    bad = sorted(program.declared_tools - allowed)
    return "rejected " + str(bad) if bad else "accepted"


# ---------------------------------------------------------------- theorem checks
def check_T1():
    lines = []
    for p, k in ((0.7, 3), (0.7, 8), (0.3, 8), (0.05, 8)):
        sim_mean, sim_fail = simulate_attempts(p, k, 20000, seed=k)
        lines.append(f"p={p:.2f} k={k}: E[attempts] formula {expected_attempts(p, k):.4f} sim {sim_mean:.4f}; "
                     f"P(all fail) formula {(1 - p) ** k:.4f} sim {sim_fail:.4f}")
    lines.append(f"no budget, p=0.7: E[attempts] = 1/p = {1 / 0.7:.4f}; stuck loop p=0: cost grows as k -> "
                 + ", ".join(f"k={k}: {expected_attempts(0.0, k):.0f}" for k in (8, 100, 10000)))
    const = [0.7] * 20
    lines.append(f"independent failures (p=0.7 each), call 1, give-up 20: p*C_fail = 14 > 1 so every retry pays: "
                 f"k*={best_budget(const, 1.0, 20.0)} of 20, cost {retry_cost_seq(const, 1.0, 20.0):.4f}")
    decay = [0.7 * 0.5**i for i in range(20)]
    k = best_budget(decay, 1.0, 20.0)
    lines.append(f"correlated failures (p_i = 0.7 * 0.5^i): retry while p_i*20 >= 1 -> k*={k}; cost k=1 {retry_cost_seq(decay[:1], 1.0, 20.0):.4f}, "
                 f"k*={k} {retry_cost_seq(decay[:k], 1.0, 20.0):.4f}, k=20 {retry_cost_seq(decay, 1.0, 20.0):.4f}")
    reach = [1.0]
    for p in decay:
        reach.append(reach[-1] * (1 - p))
    lines.append("saving from allowing attempt i = P(reach i) * (p_i*C_fail - c): " + ", ".join(
        f"{i + 1}:{reach[i] * (decay[i] * 20 - 1):+.4f}" for i in range(6)))
    return lines


def check_T2():
    lines = []
    V, policy, iters = value_iteration(MDP, gamma=0.95)
    closed = (0.75 * 9 - 0.20 * 1 - 0.05 * 51) / (1 - 0.95 * 0.20)
    lines.append(f"value iteration (gamma 0.95, p_harm 0.05): V(open) = {V['open']:.4f}, policy = {policy['open']}, {iters} iterations")
    lines.append(f"closed form for 'always auto': (0.75*9 - 0.20*1 - 0.05*51)/(1 - 0.95*0.20) = {closed:.4f}; escalate = 4; close = -5")
    rnd = random.Random(0)
    worst = 0.0
    for _ in range(1000):
        U = {s: rnd.uniform(-100, 100) for s in MDP}
        W = {s: rnd.uniform(-100, 100) for s in MDP}
        TU, _ = bellman(U, MDP, 0.95)
        TW, _ = bellman(W, MDP, 0.95)
        worst = max(worst, max(abs(TU[s] - TW[s]) for s in MDP) / max(abs(U[s] - W[s]) for s in MDP))
    lines.append(f"contraction: max ||TU - TW|| / ||U - W|| over 1000 random pairs = {worst:.4f} <= gamma 0.95")
    for ph in (0.02, 0.05, 0.06, 0.07, 0.10):
        Vh, pol, _ = value_iteration(make_mdp(ph), gamma=0.95)
        lines.append(f"p(wrong refund)={ph:.2f}: V(open) {Vh['open']:.4f} -> {pol['open']}")
    lines.append(f"break-even p_harm where auto = escalate: (7 - 4*0.81)/60 = {(7 - 4 * 0.81) / 60:.4f}")
    return lines


def check_T3():
    lines = []
    d_bfs, e_bfs = bfs(GRID)
    c1, p1, e1 = grid_astar(GRID, 1.0)
    c0, _, e0 = grid_astar(GRID, 0.0)
    c5, _, e5 = grid_astar(GRID, 5.0)
    lines.append(f"grid: BFS shortest {d_bfs} steps ({e_bfs} expanded); A* h=0 (Dijkstra) {c0} ({e0} expanded); "
                 f"A* Manhattan {c1} ({e1} expanded); A* 5x Manhattan {c5} ({e5} expanded)")
    succ = lambda n: PLAN[n]
    for name, h in (("zero", lambda n: 0), ("admissible", H_ADMISSIBLE.get), ("overestimating", H_OVERESTIMATE.get)):
        cost, path, exp = astar("start", "draft_reply", succ, h)
        lines.append(f"plan graph, h={name}: cost {cost} via {' -> '.join(path)} ({exp} expanded)")
    true = {n: astar(n, "draft_reply", succ, lambda m: 0)[0] for n in PLAN}
    lines.append("h* (true cost-to-go): " + ", ".join(f"{n}={true[n]}" for n in PLAN)
                 + f"; admissible h <= h* everywhere: {all(H_ADMISSIBLE[n] <= true[n] for n in PLAN)}; "
                 f"overestimate violates at: {[n for n in PLAN if H_OVERESTIMATE[n] > true[n]]}")
    return lines


def check_T4():
    lines = []
    for n in (6, 27, 97):
        prog = collatz_then_delete(n)
        verdicts = [dynamic_check(prog, b) for b in (10, 100, 1000)]
        steps = sum(1 for kind, _ in prog() if kind == "step")
        lines.append(f"collatz_then_delete({n}): halts after {steps} steps; budget 10/100/1000 -> {verdicts}")
    lines.append(f"never_deletes: dynamic {dynamic_check(never_deletes(), 1000)}; allow-list {allow_list_check(never_deletes())} (conservative)")
    lines.append(f"collatz_then_delete(27): allow-list {allow_list_check(collatz_then_delete(27))} without running it")
    return lines


CHECKS = {"T1": check_T1, "T2": check_T2, "T3": check_T3, "T4": check_T4}


def demo():
    auto = expected_utility([(0.97, 2.0), (0.03, -40.0)])
    review = expected_utility([(1.0, 2.0 - 1.5)])
    print(f"refund under 50: auto-approve EU {auto:.2f} vs human review EU {review:.2f} -> {'auto' if auto > review else 'review'}")
    print(f"tool succeeds 70 %: budget 3 -> {expected_attempts(0.7, 3):.3f} calls, gives up {0.3 ** 3:.1%}")
    V, policy, _ = value_iteration(MDP)
    print(f"ticket MDP: V(open) {V['open']:.3f}, best first action {policy['open']}")
    cost, path, _ = astar("start", "draft_reply", lambda n: PLAN[n], H_ADMISSIBLE.get)
    print(f"cheapest plan: {' -> '.join(path)} (cost {cost})")
    print(f"allow-list on a program that might delete: {allow_list_check(collatz_then_delete(27))}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        print("\n".join(CHECKS[sys.argv[2]]()))
    else:
        demo()
