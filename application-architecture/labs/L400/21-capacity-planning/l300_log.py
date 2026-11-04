"""Reuse the lesson 15 request log (labs/L300/15-slo-error-budgets/traffic.py), the healthy days only."""
import importlib.util
import pathlib

L300 = pathlib.Path(__file__).resolve().parents[2] / "L300" / "15-slo-error-budgets" / "traffic.py"


def records():
    spec = importlib.util.spec_from_file_location("l300_traffic", L300)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.requests(incident=False))  # the incident is lesson 15's fault, not normal demand
