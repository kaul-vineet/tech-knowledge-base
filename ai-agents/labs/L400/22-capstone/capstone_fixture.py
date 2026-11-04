"""Shared test fixture for the capstone milestones: fake model, effects service, one MCP server, a temp SQLite dir."""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import effects_service  # noqa: E402
import fake_server_l400  # noqa: E402
import triage  # noqa: E402
import workflow  # noqa: E402

INCIDENTS = {i["id"]: i for i in json.loads((HERE / "fixtures" / "incidents.json").read_text(encoding="utf-8"))}


class Env:
    def __init__(self):
        self.model, self.model_url = fake_server_l400.start_in_thread()
        self.effects, self.effects_url = effects_service.start_in_thread()
        self.mcp = triage.start_mcp()
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.clock = workflow.Clock(0)

    def agent(self, endpoints=None, crash_at=(), db="t.db"):
        return triage.Triage(endpoints or [(self.model_url, "fake-model")], self.model_url, self.effects_url,
                             Path(self.tmp.name) / db, Path(self.tmp.name) / "trace.jsonl", clock=self.clock,
                             crash_at=crash_at, mcp=self.mcp)

    def effects_list(self):
        import requests
        return requests.get(f"{self.effects_url}/effects", timeout=5).json()

    def close(self):
        self.mcp.close()
        for s in (self.model, self.effects):
            s.shutdown()
            s.server_close()
        self.tmp.cleanup()
