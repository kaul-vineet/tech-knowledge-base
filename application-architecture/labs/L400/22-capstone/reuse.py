"""Load earlier labs' modules by path instead of copying them (capstone reuses L200-L400 code as-is).

Each module is imported from its own lab folder, so a fix in the lesson is a fix in the capstone.
"""
import importlib.util
import pathlib
import sys

LABS = pathlib.Path(__file__).resolve().parents[2]


def load(relative, name):
    path = LABS / relative
    lab_folder = path.parent.parent if path.parent.name == "solution" else path.parent
    sys.path.insert(0, str(lab_folder))  # the module's own sibling imports (e.g. legacy_monolith, events)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(lab_folder))
    return module


strangler = load("L400/17-strangler-fig/strangler.py", "cap_strangler")  # facade, parallel run, cut-over
fines_fixed = load("L400/17-strangler-fig/solution/fines_service.py", "cap_fines_fixed")
fines_buggy = load("L400/17-strangler-fig/fines_service.py", "cap_fines_buggy")  # seeded fault
fines_traffic = load("L400/17-strangler-fig/traffic.py", "cap_fines_traffic")
fitness_legacy = load("L400/17-strangler-fig/fitness_legacy.py", "cap_fitness_legacy")
tenancy = load("L400/18-multi-tenancy/tenancy.py", "cap_tenancy")  # TenantGuard, Session
fitness_tenant = load("L400/18-multi-tenancy/fitness_tenant.py", "cap_fitness_tenant")
rego_lite = load("L400/19-policy-as-code/rego_lite.py", "cap_rego_lite")  # policy engine + decision log
fitness_policy = load("L400/19-policy-as-code/fitness_policy.py", "cap_fitness_policy")
POLICY_FIXED = LABS / "L400/19-policy-as-code/solution/loans.rego"
POLICY_BUGGY = LABS / "L400/19-policy-as-code/policy/loans.rego"  # seeded fault
events = load("L200/09-event-driven-integration/events.py", "cap_events")
outbox = load("L200/09-event-driven-integration/outbox.py", "cap_outbox")  # Relay (polling publisher)
bus = load("L200/09-event-driven-integration/bus.py", "cap_bus")
consumers = load("L200/09-event-driven-integration/consumers.py", "cap_consumers")  # idempotent consumers
contract = load("L300/14-consumer-driven-contracts/solution/contract.py", "cap_contract")  # body + matchers
slo = load("L300/15-slo-error-budgets/solution/slo.py", "cap_slo")  # SLIs incl. latency, burn-rate alerts
capacity = load("L400/21-capacity-planning/solution/capacity.py", "cap_capacity")
fitness_capacity = load("L400/21-capacity-planning/fitness_capacity.py", "cap_fitness_capacity")
