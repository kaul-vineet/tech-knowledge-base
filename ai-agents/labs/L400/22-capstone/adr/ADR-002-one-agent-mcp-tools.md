# ADR-002: One triage agent with read-only MCP tools, not a multi-agent system

## Status
Accepted (2026-10-28). Evidence: lesson 17 (ADR-0017).

## Context
Triage needs metrics, logs, deploy age and runbooks for one service: a small, fixed tool set and short results (7 log lines). Lesson 17 showed that routers and planner/executor designs failed cross-domain and observation-dependent tasks, and supervisor/worker doubled model calls; one agent was enough unless the context overflowed.

## Decision
We will use one agent whose facts come from code-driven MCP calls (`get_metrics`, `get_recent_logs`, `get_last_deploy`) and one model call that proposes the triage. Side-effecting actions are not MCP tools: they run only from the durable workflow after the policy decided them.

## Consequences
- The MCP server can be inspected and tested on its own (MCP Inspector, `test_m1_mcp_tools.py`).
- If incidents start spanning many services with long logs, apply lesson 17's estimate and escalate to workers per service.
