"""The contract between the agent and the pipeline: tool schemas (JSON Schema subset) + rules a schema cannot say.

Validated by ai-agents L200 #8 schema_check.validate BEFORE anything runs; additionalProperties false rejects
invented fields. The cross-field rule (utilisation lam/mu inside the verified envelope) is checked in code.
"""
import _kb

schema_check = _kb.load("schema_check")
RHO_MAX = 0.9  # verified envelope: M1 checks the model against the M/M/1 formula up to rho 0.9
SCENARIO = {"type": "object", "additionalProperties": False, "required": ["lam", "mu"], "properties": {
    "lam": {"type": "number", "minimum": 0.1, "maximum": 0.95},
    "mu": {"type": "number", "minimum": 0.8, "maximum": 1.5},
    "backlog": {"type": "integer", "minimum": 0, "maximum": 60},
    "customers": {"type": "integer", "minimum": 500, "maximum": 20000},
    "warmup": {"type": "integer", "minimum": 0, "maximum": 2000}}}
SCHEMAS = {
    "run_experiment": {"type": "object", "additionalProperties": False, "required": ["baseline", "candidate"],
                       "properties": {"baseline": SCENARIO, "candidate": SCENARIO,
                                      "replications": {"type": "integer", "minimum": 2, "maximum": 500},
                                      "seed": {"type": "integer", "minimum": 0, "maximum": 2 ** 31 - 1}}},
    "run_screening": {"type": "object", "additionalProperties": False, "required": ["method", "size"],
                      "properties": {"method": {"type": "string", "enum": ["morris", "sobol"]},
                                     "size": {"type": "integer", "minimum": 2, "maximum": 8192},
                                     "seed": {"type": "integer", "minimum": 0, "maximum": 2 ** 31 - 1}}}}
DESCRIPTIONS = {
    "run_experiment": "Compare two help-desk scenarios (lam = arrivals/min, mu = services/min) by simulation. "
                      "Returns means, 95% CIs and an experiment_id to cite as [exp-...].",
    "run_screening": "Global sensitivity screening of lam, mu, backlog, warmup (method morris: size = trajectories; "
                     "sobol: size = base sample N). Returns a ranking and an experiment_id."}
TOOLS = [{"type": "function", "function": {"name": n, "description": DESCRIPTIONS[n], "parameters": s}}
         for n, s in SCHEMAS.items()]


def validate(name, args):
    """Return a list of problems ([] = the proposal may be planned). Schema first, then semantic rules."""
    if name not in SCHEMAS:
        return [f"unknown tool {name!r}"]
    problems = schema_check.validate(args, SCHEMAS[name])
    if problems or name != "run_experiment":
        return problems
    for arm in ("baseline", "candidate"):
        rho = args[arm]["lam"] / args[arm]["mu"]
        if rho > RHO_MAX:
            problems.append(f"$.{arm}: utilisation lam/mu = {rho:.3f} is outside the verified envelope "
                            f"(<= {RHO_MAX})")
    return problems
