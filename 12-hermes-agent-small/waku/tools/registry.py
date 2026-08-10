"""Tool registry — the 'Agentic Tools' box on the whiteboard.

A tool is three things: a name+description the model reads, a JSON schema for
its arguments, and a Python function that runs. That's it. (Registry pattern
adapted from launch-agentic-rag's app/agents/tools/registry.py.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    fn: Callable[..., str]  # tools return a string the model observes

    def to_api(self) -> dict[str, Any]:
        """The shape the Messages API expects in its `tools=` parameter."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict[str, Any]]:
        return [t.to_api() for t in self._tools.values()]

    def execute(self, name: str, args: dict[str, Any]) -> str:
        """Run one tool call safely: the model observes errors as text instead
        of crashing the loop (execute_tool_safely pattern)."""
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'"
        try:
            return tool.fn(**args)
        except Exception as exc:  # surface, don't crash — the model can retry
            return f"Error running {name}: {exc}"
