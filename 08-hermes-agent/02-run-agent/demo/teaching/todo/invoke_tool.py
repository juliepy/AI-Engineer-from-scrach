# =============================================================================
# invoke_tool — 对照 agent/agent_runtime_helpers.py · invoke_tool
# =============================================================================
# 保留：agent 级工具截胡（todo）→ 其余走 registry.dispatch
# 省略：plugin block、memory、session_search、clarify、delegate 等旁路
# =============================================================================
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from registry import registry


def invoke_tool(
    agent: Any,
    function_name: str,
    function_args: dict,
    effective_task_id: str = "",
    tool_call_id: Optional[str] = None,
    messages: list = None,
) -> str:
    """Invoke a single tool and return the result string.

    Handles both agent-level tools (todo, …) and registry-dispatched tools.
    """
    if not isinstance(function_args, dict):
        function_args = {}

    # ── Agent-level intercept（AGENTS.md: todo/memory 与会话状态紧耦合）──
    if function_name == "todo":
        from todo_tool import todo_tool as _todo_tool

        return _todo_tool(
            todos=function_args.get("todos"),
            merge=function_args.get("merge", False),
            store=agent._todo_store,
        )

    # ── 普通工具：registry 分发 ──────────────────────────────────────────
    entry = registry.get(function_name)
    if entry is None:
        return json.dumps(
            {"error": f"Unknown tool: {function_name}"},
            ensure_ascii=False,
        )
    return registry.dispatch(
        function_name,
        function_args,
        task_id=effective_task_id,
        tool_call_id=tool_call_id,
        store=getattr(agent, "_todo_store", None),
    )
