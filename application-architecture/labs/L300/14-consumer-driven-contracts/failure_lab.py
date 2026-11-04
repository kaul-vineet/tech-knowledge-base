"""Lesson 14 failureLab: the provider renames `title` to `name`. Which check notices?

Run: python failure_lab.py
"""
import importlib.util
import json
import pathlib
import urllib.request

import contract as base
import provider
from consumer import CatalogueClient, loan_receipt
from test_consumer import StubClient

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = HERE / "contracts" / "loans-service--catalogue-service.json"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checks(verifier, title_field="name"):
    """Run every check the two teams have against a provider that uses `title_field`."""
    results = {}
    server, url = provider.start(title_field=title_field)  # fault: the provider team "tidies up" a field name
    with urllib.request.urlopen(url + "/books/b1", timeout=5) as resp:  # provider unit test, updated with the rename
        results["provider unit test"] = "PASS" if json.loads(resp.read())[title_field] == "Dune" else "FAIL"
    results["consumer unit test (stub)"] = "PASS" if "Dune" in loan_receipt(StubClient(), "m1", "b1") else "FAIL"
    try:
        loan_receipt(CatalogueClient(url), "m1", "b1")
        results["consumer in production"] = "PASS"
    except KeyError as exc:
        results["consumer in production"] = f"FAIL KeyError: {exc}"
    server.shutdown()
    server.server_close()
    server, url = provider.start(title_field=title_field, states=True)
    problems = verifier.verify_provider(CONTRACT, url)
    results["contract verification"] = "PASS" if not problems else f"FAIL {problems}"
    server.shutdown()
    server.server_close()
    return results


def main():
    solution = load(HERE / "solution" / "contract.py", "contract_solution")
    for label, verifier in [("base verifier (status only)", base), ("solution verifier (body + matchers)", solution)]:
        print(f"provider renames title -> name; {label}:")
        for check, outcome in checks(verifier).items():
            print(f"    {check:<27} {outcome}")


if __name__ == "__main__":
    main()
