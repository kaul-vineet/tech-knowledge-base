"""Threat model as code: a data-flow diagram (elements, zones, flows), STRIDE threats, controls, and the TESTS that
prove each control. The checker answers "did we do a good enough job?" (OWASP's 4th question) with evidence."""
import ast
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOPIC = HERE.parents[2]  # the cryptography/ folder; test references are relative to it
SEED = 21  # seeds the injected model drift (which control's test disappears)
APPLIES = {"external": "SR", "process": "STRIDE", "store": "TID", "flow": "TID"}  # STRIDE-per-element table used here


def load(path=HERE / "model.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def candidates(model) -> list:
    """Every (element, STRIDE letter) pair the table says to consider: the brainstorming checklist."""
    return [(name, c) for name, e in model["elements"].items() for c in APPLIES[e["type"]]]


def crosses_boundary(model, flow: dict) -> bool:
    els = model["elements"]
    return els[flow["from"]]["zone"] != els[flow["to"]]["zone"]


def test_exists(ref: str) -> bool:
    """'labs/.../test_x.py::Class::method' -> does that test function exist (AST, no import)?"""
    file, cls, meth = ref.split("::")
    path = TOPIC / file
    if not path.is_file():
        return False
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            return any(isinstance(f, ast.FunctionDef) and f.name == meth for f in node.body)
    return False


def check(model) -> list:
    problems = []
    for t in model["threats"]:
        el = model["elements"].get(t["element"])
        if el is None:
            problems.append(f"{t['id']}: unknown element {t['element']}")
        elif t["stride"] not in APPLIES[el["type"]]:
            problems.append(f"{t['id']}: {t['stride']} does not apply to a {el['type']}")
        if not t["controls"] and not t.get("accepted"):
            problems.append(f"{t['id']}: no control and no recorded acceptance")
        problems += [f"{t['id']}: unknown control {c}" for c in t["controls"] if c not in model["controls"]]
    # BUG on purpose: a control counts as soon as it is NAMED - nobody checks that its tests still exist, and
    # nobody checks that every element (e.g. a newly added boundary-crossing flow) has threats at all
    return problems


def verified_controls(model) -> set:
    return set(model["controls"])  # (the unfixed checker trusts every named control)


def cheapest(node: dict, verified: set):
    """Attack tree: OR = cheapest child, AND = sum of children; a leaf behind a verified control is closed (inf)."""
    if "children" not in node:
        return (float("inf"), []) if node.get("control") in verified else (node["cost"], [node["name"]])
    kids = [cheapest(c, verified) for c in node["children"]]
    if node["type"] == "OR":
        return min(kids, key=lambda k: k[0])
    return sum(k[0] for k in kids), [step for k in kids for step in k[1]]


def tree_controls(node: dict) -> set:
    return {node["control"]} if "control" in node else set().union(*(tree_controls(c) for c in node.get("children", [])))


def mermaid(model) -> str:
    lines = ["flowchart LR"]
    for zone, label in model["boundaries"].items():
        lines.append(f'  subgraph {zone}["{label}"]')
        lines += [f"    {n.replace('-', '_')}[{n}]" for n, e in model["elements"].items() if e["type"] != "flow" and e["zone"] == zone]
        lines.append("  end")
    for name, e in model["elements"].items():
        if e["type"] == "flow":
            ids = sorted(t["id"] for t in model["threats"] if t["element"] == name)
            lines.append(f"  {e['from'].replace('-', '_')} -->|{','.join(ids) or 'NO THREATS'}| {e['to'].replace('-', '_')}")
    return "\n".join(lines)


def inject_drift(model, rng) -> str:
    """Two everyday changes: a refactor deletes a test, and a new integration adds a flow nobody modelled."""
    victim = rng.choice(sorted(tree_controls(model["attack_tree"])))
    model["controls"][victim]["tests"] = [model["controls"][victim]["tests"][0].rsplit("::", 1)[0] + "::test_removed_in_refactor"]
    model["elements"]["siem"] = {"type": "external", "zone": "internet"}
    model["elements"]["app-log->siem"] = {"type": "flow", "from": "app-log", "to": "siem"}
    return victim


if __name__ == "__main__":
    if "--mermaid" in sys.argv:
        print(mermaid(load()))
        sys.exit(0)
    m = load()
    flows = [n for n, e in m["elements"].items() if e["type"] == "flow"]
    print(f"1) elements {len(m['elements'])} (flows {len(flows)}, crossing a boundary "
          f"{sum(crosses_boundary(m, m['elements'][f]) for f in flows)}) | STRIDE-per-element candidates {len(candidates(m))}"
          f" | threats {len(m['threats'])} | controls {len(m['controls'])}")
    print("2) checker problems:", check(m), "| controls whose tests exist:",
          f"{sum(all(test_exists(r) for r in c['tests']) for c in m['controls'].values())}/{len(m['controls'])}")
    cost, path = cheapest(m["attack_tree"], verified_controls(m))
    print(f"3) cheapest open attack path: cost {cost} via {path}")
    print("--- fault: model drift (a test is deleted in a refactor; a SIEM export flow is added)")
    victim = inject_drift(m, random.Random(SEED))
    print(f"control {victim} now points at a missing test: {not test_exists(m['controls'][victim]['tests'][0])} | "
          f"checker problems: {check(m)} | new flow app-log->siem threats: "
          f"{[t['id'] for t in m['threats'] if t['element'] == 'app-log->siem']}")
