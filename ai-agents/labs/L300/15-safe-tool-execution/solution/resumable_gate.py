"""Build task (lesson 15): resume after a crash - rows stuck in 'executing' are re-sent with their ORIGINAL key."""
import json

from safe_tools import ToolGate


class ResumableGate(ToolGate):
    def resume(self):
        done = []
        for row_id, args, key in self.db.execute(
                "SELECT id, args, idem_key FROM approvals WHERE status = 'executing' ORDER BY id").fetchall():
            result = self._send(json.loads(args), key)  # same key -> the payments API replays, no second refund
            self.db.execute("UPDATE approvals SET status = 'done', result = ? WHERE id = ?", (json.dumps(result), row_id))
            self.audit("executor", "resumed", approval=row_id, key=key, result=result)
            done.append(result)
        return done
