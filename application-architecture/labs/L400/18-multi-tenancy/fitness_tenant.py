"""Fitness function (lesson 18): no query on a tenant table without a tenant id. Run: python fitness_tenant.py

Static half: every SQL string constant that touches a tenant table must bind tenant_id
(SELECT/UPDATE/DELETE: `WHERE tenant_id = ?`; INSERT: a tenant_id column). The runtime half is TenantGuard.
"""
import ast
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
TENANT_TABLES = re.compile(r"\b(FROM|UPDATE|INTO|JOIN)\s+(\{table\}|loans\w*)", re.I)


def unscoped_queries(path):
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and TENANT_TABLES.search(node.value):
            sql = node.value
            if not sql.lstrip().upper().startswith(("SELECT", "UPDATE", "DELETE", "INSERT")):
                continue  # docstrings and DDL are not data access
            scoped = "tenant_id" in sql if sql.lstrip().upper().startswith("INSERT") else \
                re.search(r"\bWHERE\s+tenant_id\s*=\s*\?", sql, re.I)
            if not scoped:
                found.append(f"{path.name}:{node.lineno} {sql}")
    return found


def gate(files=(HERE / "repository.py",)):
    found = [q for f in files for q in unscoped_queries(pathlib.Path(f))]
    return {"gate": "tenant-scoped-queries", "ok": not found, "value": found, "budget": 0}


if __name__ == "__main__":
    result = gate()
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)
