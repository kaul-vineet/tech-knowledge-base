"""Build-task solution: the inventory also reports cryptography modules that are loaded BY NAME at run time.

Flags importlib.import_module(X) / __import__(X) when X is a string constant, or a module-level name bound to a string
constant or to os.environ.get(..., "<constant default>"), that names cryptography.hazmat.primitives.*.
Run from the lab folder: python solution/inventory_dynamic.py
"""
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import inventory as base  # noqa: E402

LOADERS = {"importlib.import_module", "import_module", "__import__"}
USAGE = {"x25519": "key-establishment", "x448": "key-establishment", "ec": "key-establishment", "dh": "key-establishment",
         "mlkem": "key-establishment", "ed25519": "signature", "ed448": "signature", "dsa": "signature",
         "mldsa": "signature", "rsa": "unknown"}


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        inner = dotted(node.value)
        return f"{inner}.{node.attr}" if inner else None
    return None


def string_value(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and dotted(node.func) in ("os.environ.get", "os.getenv") and len(node.args) == 2:
        return string_value(node.args[1])                       # the default is what runs when the variable is unset
    return None


def module_constants(tree):
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and string_value(node.value):
            out.update({t.id: string_value(node.value) for t in node.targets if isinstance(t, ast.Name)})
    return out


def scan_dynamic(path, rel):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    consts, found = module_constants(tree), []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and dotted(node.func) in LOADERS and node.args):
            continue
        arg = node.args[0]
        name = consts.get(arg.id) if isinstance(arg, ast.Name) else string_value(arg)
        if name and name.startswith("cryptography.hazmat.primitives"):
            found.append({"file": rel, "line": node.lineno, "algorithm": f"dynamic: {name}",
                          "usage": USAGE.get(name.rsplit(".", 1)[-1], "unknown")})
    return found


def scan_python(path, rel):
    return base.scan_python(path, rel) + scan_dynamic(path, rel)


def scan(stage="before", messaging="migrated/messaging"):
    return base.scan(stage, messaging, python_scanner=scan_python)


if __name__ == "__main__":
    import json
    for f in scan("after", "faults/messaging_bypass"):
        if f["service"] == "messaging":
            print(json.dumps(f))
