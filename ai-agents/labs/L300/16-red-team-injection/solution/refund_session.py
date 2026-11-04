"""Build task (lesson 16): a refund session. send_refund is allowed, so the allow-list no longer helps:
provenance must hold for every argument, and even then the call is only QUEUED for a human (lesson 15)."""
from redteam_agent import Policy


class RefundPolicy(Policy):
    ALLOWED = Policy.ALLOWED | {"send_refund"}
    NEEDS_APPROVAL = {"send_refund"}

    def __init__(self, task):
        super().__init__(task)
        self.queue = []

    def check(self, name, args):
        reason = super().check(name, args)
        if reason is None and name in self.NEEDS_APPROVAL:
            self.queue.append((name, args))
            return "queued for human approval (see lesson 15); not executed"
        return reason
