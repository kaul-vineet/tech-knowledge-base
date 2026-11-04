"""Build task (lesson 15) - YOUR FILE. Shipped UNFIXED: resume() re-sends rows stuck in 'executing' with a NEW
key, so the payments API sees a new request and refunds a second time.

TODO: send each stuck row with its ORIGINAL idem_key (the payments API then replays the stored result),
write status 'done' and an audit row 'resumed'.
Check it: BUILD_TARGET=mine python -m unittest -v test_build_task
"""
import json
import uuid

from safe_tools import ToolGate


class ResumableGate(ToolGate):
    def resume(self):
        done = []
        for row_id, args in self.db.execute(
                "SELECT id, args FROM approvals WHERE status = 'executing' ORDER BY id").fetchall():
            result = self._send(json.loads(args), uuid.uuid4().hex)  # fresh key: looks like a new refund
            self.db.execute("UPDATE approvals SET status = 'done', result = ? WHERE id = ?", (json.dumps(result), row_id))
            done.append(result)
        return done
