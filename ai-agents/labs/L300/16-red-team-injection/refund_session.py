"""Build task (lesson 16) - YOUR FILE. Shipped UNFIXED: the refund session just adds send_refund to the
allow-list, so a legitimate refund runs straight away - the agent moves money with nobody approving it.
(Provenance from Policy.check still blocks the injected 900; the gap is the missing approval step.)

TODO: keep super().check() first; if it allows a NEEDS_APPROVAL tool, append (name, args) to self.queue and
return "queued for human approval (see lesson 15); not executed" instead of None.
Check it: BUILD_TARGET=mine python -m unittest -v test_build_task
"""
from redteam_agent import Policy


class RefundPolicy(Policy):
    ALLOWED = Policy.ALLOWED | {"send_refund"}
    NEEDS_APPROVAL = {"send_refund"}  # declared, not enforced yet

    def __init__(self, task):
        super().__init__(task)
        self.queue = []
