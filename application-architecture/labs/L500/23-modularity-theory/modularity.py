"""Lesson 23 - modularity theory, computed: dependency graphs, cycles, strict layering, Martin's I/A/D metrics.

Everything here is stdlib only. Graphs are (nodes, edges) with edges as (from, to) = "from depends on to".
The Library Loans graphs are read from the real lab code with ast (no import side effects).
"""
import ast
import math
import pathlib
import random

LABS = pathlib.Path(__file__).resolve().parents[2]
HEXAGONAL = LABS / "L200" / "07-hexagonal-architecture"
LAYERED = LABS / "L100" / "02-layered-structure"
SKIP = ("test_", "try_it")
ABSTRACT_BASES = {"Protocol", "ABC"}


def is_main_block(node):
    """True for `if __name__ == "__main__":` - script wiring, not part of the module's import-time dependencies."""
    test = getattr(node, "test", None)
    return (isinstance(node, ast.If) and isinstance(test, ast.Compare) and isinstance(test.left, ast.Name)
            and test.left.id == "__name__" and any(isinstance(c, ast.Constant) and c.value == "__main__"
                                                    for c in test.comparators))


def walk(tree, include_main):
    """ast.walk that can skip the __main__ block."""
    todo = [tree]
    while todo:
        node = todo.pop()
        yield node
        todo.extend(child for child in ast.iter_child_nodes(node) if include_main or not is_main_block(child))


def module_graph(lab_dir, include_main=False):
    """Return (nodes, edges, classes) for the top-level modules of a lab (tests, try_it and solution/ excluded).

    include_main=False ignores imports inside `if __name__ == "__main__":` (script entry wiring).

    classes[m] = (total classes, abstract classes); a class is abstract if it derives from Protocol/ABC
    or declares an @abstractmethod.
    """
    lab_dir = pathlib.Path(lab_dir)
    files = sorted(p for p in lab_dir.glob("*.py") if not p.name.startswith(SKIP))
    nodes = [p.stem for p in files]
    edges, classes = set(), {}
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        total = abstract = 0
        for node in walk(tree, include_main):
            if isinstance(node, ast.Import):
                targets = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                targets = [node.module.split(".")[0]]
            else:
                targets = []
            for target in targets:
                if target in nodes and target != path.stem:
                    edges.add((path.stem, target))
            if isinstance(node, ast.ClassDef):
                total += 1
                bases = {getattr(b, "id", getattr(b, "attr", "")) for b in node.bases}
                has_abstract_method = any(
                    isinstance(d, ast.Name) and d.id == "abstractmethod" or
                    isinstance(d, ast.Attribute) and d.attr == "abstractmethod"
                    for f in node.body if isinstance(f, ast.FunctionDef) for d in f.decorator_list)
                abstract += bool(bases & ABSTRACT_BASES or has_abstract_method)
        classes[path.stem] = (total, abstract)
    return nodes, sorted(edges), classes


def successors(nodes, edges):
    succ = {n: [] for n in nodes}
    for a, b in edges:
        succ[a].append(b)
    return succ


def tarjan_scc(nodes, edges):
    """Strongly connected components (Tarjan 1972), iterative so large random graphs do not hit the recursion limit."""
    succ = successors(nodes, edges)
    index, low, on_stack, stack, comps, counter = {}, {}, set(), [], [], [0]
    for root in nodes:
        if root in index:
            continue
        work = [(root, iter(succ[root]))]
        index[root] = low[root] = counter[0]
        counter[0] += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(succ[w])))
                    advanced = True
                    break
                if w in on_stack:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = set()
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.add(w)
                    if w == v:
                        break
                comps.append(frozenset(comp))
    return comps


def is_acyclic(nodes, edges):
    """Kahn's algorithm: a graph is acyclic iff every node can be removed in topological order."""
    indeg = {n: 0 for n in nodes}
    for _, b in edges:
        indeg[b] += 1
    succ = successors(nodes, edges)
    ready = [n for n in nodes if indeg[n] == 0]
    removed = 0
    while ready:
        n = ready.pop()
        removed += 1
        for m in succ[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
    return removed == len(nodes)


def condensation(nodes, edges):
    comps = tarjan_scc(nodes, edges)
    owner = {n: i for i, comp in enumerate(comps) for n in comp}
    cedges = sorted({(owner[a], owner[b]) for a, b in edges if owner[a] != owner[b]})
    return list(range(len(comps))), cedges, comps


def longest_path_layering(nodes, edges):
    """l(v) = length of the longest path from v to a sink; defined only for acyclic graphs (the converse proof)."""
    if not is_acyclic(nodes, edges):
        raise ValueError("graph has a cycle: no strict layering exists")
    succ, level = successors(nodes, edges), {}

    def visit(v):
        if v not in level:
            level[v] = 1 + max((visit(w) for w in succ[v]), default=-1)
        return level[v]

    for n in nodes:
        visit(n)
    return level


def strict_layering_violations(edges, level):
    """Strict layering: every dependency points to a strictly lower layer, l(from) > l(to)."""
    return [(a, b) for a, b in edges if not level[a] > level[b]]


def martin_metrics(nodes, edges, classes):
    """Martin (1994) per component: Ca, Ce, I = Ce/(Ca+Ce), A = abstract/total, Dn = |A + I - 1|."""
    rows = {}
    for n in nodes:
        ca = sum(1 for a, b in edges if b == n)
        ce = sum(1 for a, b in edges if a == n)
        total, abstract = classes[n]
        i = ce / (ca + ce) if ca + ce else 0.0
        a = abstract / total if total else 0.0  # convention: a module with no classes counts as concrete
        rows[n] = {"Ca": ca, "Ce": ce, "I": i, "A": a, "Dn": abs(a + i - 1)}
    return rows


def distance_to_main_sequence_numeric(a, i, steps=200_000):
    """Brute force: minimum Euclidean distance from (I, A) to points (t, 1 - t) of the main sequence."""
    return min(math.hypot(i - t, a - (1 - t)) for t in (k / steps for k in range(steps + 1)))


def random_graph(rng, n, p, strict=True):
    """Random graph with a random layer per node; strict=True keeps only edges to strictly lower layers."""
    nodes = list(range(n))
    level = {v: rng.randrange(max(1, n // 3)) for v in nodes}
    edges = [(a, b) for a in nodes for b in nodes
             if a != b and rng.random() < p and (level[a] > level[b] if strict else level[a] >= level[b])]
    return nodes, edges, level


# Parnas 1972 KWIC example, modelled as "which modules know which design decision".
# This mapping is OUR reading of the paper's argument (lesson 27 asks you to check it against the paper).
KWIC_DECISIONS = ["input format", "all lines in core", "packing 4 chars/word", "index of shifts", "alphabetize once"]
KWIC_CONVENTIONAL = {
    "Input": {"input format", "all lines in core", "packing 4 chars/word"},
    "Circular Shift": {"all lines in core", "packing 4 chars/word", "index of shifts"},
    "Alphabetizing": {"all lines in core", "packing 4 chars/word", "index of shifts", "alphabetize once"},
    "Output": {"all lines in core", "packing 4 chars/word", "index of shifts", "alphabetize once"},
    "Master Control": set(),
}
KWIC_HIDING = {
    "Line Storage": {"all lines in core", "packing 4 chars/word"},
    "Input": {"input format"},
    "Circular Shifter": {"index of shifts"},
    "Alphabetizer": {"alphabetize once"},
    "Output": set(),
    "Master Control": set(),
}


def change_impact(knows):
    """Modules that must change when a decision changes = modules that know that decision."""
    return {d: sorted(m for m, ds in knows.items() if d in ds) for d in KWIC_DECISIONS}
