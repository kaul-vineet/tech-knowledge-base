"""Build task: how many replications per arm before the pipeline may draw a conclusion?

Shipped UNFIXED: it trusts the agent's request (3), so conclusions rest on whatever noise 3 runs produced.
Make required_replications() return the number per arm needed for a 95% CI on the difference with half-width
<= half_width: at least N0 = 10 pilot runs, then n * (achieved half-width / target)^2, rounded up.
Check: BUILD_TARGET=mine python -m unittest tests.test_build_task -v
"""
N0 = 10


def required_replications(requested, a, b, half_width):
    return requested
