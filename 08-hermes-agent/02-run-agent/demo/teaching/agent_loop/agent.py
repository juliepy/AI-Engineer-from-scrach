# =============================================================================
# DemoAgent — 最小假 AIAgent（对照 run_agent.AIAgent）
# =============================================================================
# 保留：run_conversation forwarder、_todo_store、tools schema、budget 字段
# 省略：provider 路由、session DB、压缩、gateway callbacks…
# =============================================================================
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from conversation_loop import run_conversation as _run_conversation
from iteration_budget import IterationBudget
from registry import registry
from todo_tool import TodoStore

# 触发顶层 registry.register（对照 model_tools import → discover）
import todo_tool  # noqa: F401
import web_search_tool  # noqa: F401


class DemoAgent:
    """教学版 AIAgent：只填主循环会摸到的字段。"""

    def __init__(
        self,
        *,
        chat_with_tools: Callable,
        system_prompt: str,
        enabled_tools: Optional[List[str]] = None,
        max_iterations: int = 10,
        model: str = "deepseek-v4-pro",
        quiet_mode: bool = False,
    ):
        self._chat_with_tools = chat_with_tools
        self._cached_system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.model = model
        self.provider = "deepseek"
        self.quiet_mode = quiet_mode
        self.session_id = "demo-agent-loop"
        self.platform = "demo"

        # ── 工具 schema（对照 get_tool_definitions → agent.tools）────────
        names = enabled_tools or ["todo", "web_search"]
        self.tools = registry.get_definitions(names, quiet_mode=quiet_mode)
        self.valid_tool_names = {t["function"]["name"] for t in self.tools}

        # ── agent 级状态（todo 截胡依赖）────────────────────────────────
        self._todo_store = TodoStore()

        # ── 循环运行时字段（run_conversation 会重置 budget）──────────────
        self.iteration_budget = IterationBudget(max_iterations)
        self._budget_grace_call = False
        self._interrupt_requested = False
        self._api_call_count = 0
        self._loop_trace = []

    def _safe_print(self, text: str) -> None:
        if not self.quiet_mode:
            print(text)

    def interrupt(self) -> None:
        """对照 AIAgent.interrupt — 下一圈 while 检查后 break。"""
        self._interrupt_requested = True

    def run_conversation(
        self,
        user_message: str,
        system_message: str = None,
        conversation_history: List[Dict[str, Any]] = None,
        task_id: str = None,
    ) -> Dict[str, Any]:
        """Forwarder — see ``agent.conversation_loop.run_conversation``."""
        return _run_conversation(
            self,
            user_message,
            system_message,
            conversation_history,
            task_id,
        )

    def chat(self, message: str) -> str:
        result = self.run_conversation(message)
        return result.get("final_response") or ""
