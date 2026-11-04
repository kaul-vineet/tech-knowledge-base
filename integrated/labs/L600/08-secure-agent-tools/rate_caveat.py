"""BUILD TASK (shipped unfixed): a 'calls < N' caveat for capability.verify(..., extra=counter.check).

A token attenuated with "calls < 3" may be used for at most 3 tool calls in its session. capability.verify() calls
extra(caveat, req) only for caveat kinds it does not know. Contract: return True (holds), False (violated) or
None (still unknown -> verify denies). Make it pass: BUILD_TARGET=mine python -m unittest tests.test_build_task
"""


class CallCounter:
    def __init__(self):
        self.used = {}  # session -> calls checked so far

    def check(self, caveat, req):
        # BUG 1: never counts - "calls < N" is accepted forever.
        # BUG 2: fails OPEN - any unknown caveat ("frobnicate = 1") is treated as satisfied.
        return True
