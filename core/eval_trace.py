from __future__ import annotations

from contextvars import ContextVar
from typing import Optional


_current_tool: ContextVar[Optional[str]] = ContextVar("current_tool", default=None)
_current_agent: ContextVar[Optional[str]] = ContextVar("current_agent", default=None)


def reset_trace() -> None:
    _current_tool.set(None)
    _current_agent.set(None)


def set_tool(tool_name: str) -> None:
    _current_tool.set(tool_name)


def set_agent(agent_name: str) -> None:
    _current_agent.set(agent_name)


def get_tool() -> Optional[str]:
    return _current_tool.get()


def get_agent() -> Optional[str]:
    return _current_agent.get()