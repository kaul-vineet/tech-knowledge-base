"""A tiny Rego-like policy engine plus a decision point with decision logs (lesson 19 lab code).

FOR LEARNING ONLY: it reads a small subset of Rego v1 (default, `name if {...}`, `name contains "msg" if {...}`,
==, !=, <, <=, >, >=, in, not, count(), input./data. paths, string/number/bool/array literals). The same
policy file runs on OPA in CI. Policy = data the service loads; the service code only asks "allowed?".
"""
import hashlib
import json
import operator
import re

RULE = re.compile(r'^(\w+)(?:\s+contains\s+("[^"]*"))?\s+if\s*\{(.*?)^\}', re.S | re.M)
DEFAULT = re.compile(r"^default\s+(\w+)\s*:=\s*(.+)$", re.M)
OPS = [" == ", " != ", " <= ", " >= ", " < ", " > ", " in "]
COMPARE = dict(zip(OPS, [operator.eq, operator.ne, operator.le, operator.ge, operator.lt, operator.gt,
                         lambda left, right: left in right]))
UNDEFINED = object()  # Rego: a missing path is undefined, and an undefined expression is false


class Policy:
    def __init__(self, text):
        self.text = text
        self.revision = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]  # logged with every decision
        self.defaults = {name: json.loads(value) for name, value in DEFAULT.findall(text)}
        self.rules = []  # (rule id, name, message or None, [conditions])
        for m in RULE.finditer(text):
            name, message, body = m.groups()
            line = text[:m.start()].count("\n") + 1
            conditions = [c.strip() for c in body.replace(";", "\n").splitlines()
                          if c.strip() and not c.strip().startswith("#")]
            self.rules.append((f"{name}@{line}", name, json.loads(message) if message else None, conditions))

    def evaluate(self, inp, data=None):
        """Returns (value of every rule name, ids of the rule bodies that matched)."""
        doc, matched, cache = {"input": inp, "data": data or {}}, [], {}

        def rule_value(name):
            if name not in cache:
                cache[name] = UNDEFINED  # guards against recursion
                bodies = [r for r in self.rules if r[1] == name]
                if bodies and bodies[0][2] is not None:  # partial set rule: collect messages
                    hits = [r for r in bodies if all(cond(c) for c in r[3])]
                    matched.extend(r[0] for r in hits)
                    cache[name] = sorted({r[2] for r in hits})
                else:  # boolean rule: any body true (bodies are OR-ed), else the default
                    hit = next((r for r in bodies if all(cond(c) for c in r[3])), None)
                    if hit:
                        matched.append(hit[0])
                    cache[name] = True if hit else self.defaults.get(name, UNDEFINED)
            return cache[name]

        def term(t):
            t = t.strip()
            if t.startswith("count(") and t.endswith(")"):
                value = term(t[6:-1])
                return UNDEFINED if value is UNDEFINED else len(value)
            if t.startswith(("input.", "data.")):
                value = doc
                for part in t.split("."):
                    value = value.get(part, UNDEFINED) if isinstance(value, dict) else UNDEFINED
                return value
            if re.fullmatch(r"\w+", t) and t not in ("true", "false") and not t.isdigit():
                return rule_value(t)
            return json.loads(t)  # "text", 5, 2.5, true, false, ["a", "b"]

        def cond(c):
            if c.startswith("not "):
                return not cond(c[4:])
            op = next((o for o in OPS if o in c), None)
            if op is None:
                return term(c) is True
            left, right = (term(x) for x in c.split(op, 1))
            if UNDEFINED in (left, right):
                return False
            try:
                return COMPARE[op](left, right)
            except TypeError:  # comparing e.g. a string with a number: undefined in Rego, false here
                return False

        values = {name: rule_value(name) for name in {r[1] for r in self.rules} | set(self.defaults)}
        return values, matched


MASK = ["/input/subject/email"]  # like OPA's system.log.mask: never write these fields to the decision log


class DecisionPoint:
    """PDP: evaluate the policy, return allowed + reasons, append one JSON line per decision.
    log_path: a file (opened per decision) or a list that collects the lines for a batched write."""

    def __init__(self, policy, log_path=None, clock=lambda: "2026-10-28T12:00:00Z"):
        self.policy, self.log_path, self.clock, self.count = policy, log_path, clock, 0

    def decide(self, inp):
        values, matched = self.policy.evaluate(inp)
        self.count += 1
        decision = {"allowed": values.get("allowed") is True, "deny": values.get("deny") or [],
                    "matched": matched}
        if self.log_path is not None:
            masked = json.loads(json.dumps(inp))
            erased = [p for p in MASK if _erase(masked, p.split("/")[2:])]
            event = {"decision_id": f"{self.policy.revision}-{self.count:06d}", "timestamp": self.clock(),
                     "path": "loans/authz/allowed", "revision": self.policy.revision, "input": masked,
                     "result": decision["allowed"], "deny": decision["deny"], "matched": matched, "erased": erased}
            if isinstance(self.log_path, list):
                self.log_path.append(json.dumps(event, sort_keys=True))
            else:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, sort_keys=True) + "\n")
        return decision


def _erase(obj, parts):
    for part in parts[:-1]:
        obj = obj.get(part) if isinstance(obj, dict) else None
    return isinstance(obj, dict) and obj.pop(parts[-1], None) is not None


def load_policy(path):
    with open(path, encoding="utf-8") as f:
        return Policy(f.read())
