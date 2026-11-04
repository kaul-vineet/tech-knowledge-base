"""Ports (application-architecture L200 #7): the host's own interfaces, named for what they are FOR.
Adapters: adapters.py (fake model over HTTP, scripted model, approver, clock, world), policy_engine.py, audit.py."""
from typing import Protocol


class ForProposingToolCalls(Protocol):
    """Driven port: the model. It PROPOSES calls (an assistant message); it never authorises anything."""

    def propose(self, messages: list, tools: list) -> dict: ...


class ForDecidingCalls(Protocol):
    """Driven port: the policy decision point. Input is built by the host from trusted sources."""

    def decide(self, inp: dict) -> dict: ...


class ForApproving(Protocol):
    """Driven port: a human. Sees the exact tool + arguments; answers yes or no."""

    def ask(self, request: dict) -> bool: ...


class ForAuditing(Protocol):
    """Driven port: the tamper-evident log."""

    def append(self, event: str, actor: str, body: dict) -> dict: ...
