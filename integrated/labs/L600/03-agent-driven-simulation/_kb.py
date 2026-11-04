"""Load modules from other topics' labs by file path (never edited, never copied).

Each source module is loaded under a unique name ("kb_<name>") so labs that happen to share a file name
(several topics have an agent_assist.py) cannot shadow each other. Paths are relative to this file (pathlib).
"""
import importlib.util
import sys
from pathlib import Path

KB = Path(__file__).resolve().parents[4]  # .../kb
SOURCES = {
    "warmup": "simulation/labs/L200/10-warmup-replications/warmup.py",          # M/M/1 help desk, Lindley rule
    "vv": "simulation/labs/L100/06-verification-validation/vv.py",              # M/M/1 formula for verification
    "sensitivity": "simulation/labs/L300/14-global-sensitivity/sensitivity.py",  # Morris screening
    "schema_check": "ai-agents/labs/L200/08-multi-tool-agent/schema_check.py",  # JSON Schema subset validator
    "resilient_agent": "ai-agents/labs/L300/14-reliability-budgets/resilient_agent.py",  # Budget (calls/tokens)
    "fake_model_server": "shared/local_agent/fake_model_server.py",            # deterministic stand-in model
}


def load(name):
    key = f"kb_{name}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, KB / SOURCES[name])
        module = importlib.util.module_from_spec(spec)
        sys.modules[key] = module
        spec.loader.exec_module(module)
    return sys.modules[key]


def source_path(name):
    return KB / SOURCES[name]
