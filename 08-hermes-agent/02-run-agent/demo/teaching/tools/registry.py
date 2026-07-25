# =============================================================================
# 教学版 Tool Registry
# 对照源码: hermes_src/tools/registry.py
# =============================================================================
# 保留：register / get_definitions / dispatch / ToolEntry
# 省略：TTL check cache、MCP override 策略、插件 shadow 拒绝、AST 发现扫描
#       （demo 里工具在 import 时直接 register，不跑 discover_builtin_tools）
# =============================================================================
from __future__ import annotations

import json
import threading
from typing import Any, Callable, Dict, List, Optional


def tool_error(message: str) -> str:
    """统一错误 JSON 字符串（源码同名 helper）。"""
    return json.dumps({"error": message}, ensure_ascii=False)


class ToolEntry:
    """Metadata for a single registered tool（对照源码 ToolEntry）。"""

    __slots__ = (
        "name",
        "toolset",
        "schema",
        "handler",
        "check_fn",
        "description",
        "emoji",
    )

    def __init__(
        self,
        name: str,
        toolset: str,
        schema: dict,
        handler: Callable,
        check_fn: Callable = None,
        description: str = "",
        emoji: str = "",
    ):
        self.name = name
        self.toolset = toolset
        self.schema = schema
        self.handler = handler
        self.check_fn = check_fn
        self.description = description or (schema.get("description") or "")
        self.emoji = emoji


class ToolRegistry:
    """Central registry — 工具在 import 时 register，主循环通过 dispatch 调用。"""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolEntry] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        toolset: str,
        schema: dict,
        handler: Callable,
        check_fn: Callable = None,
        description: str = "",
        emoji: str = "",
    ) -> None:
        """Register a tool. Called at module-import time by each tool file."""
        with self._lock:
            self._tools[name] = ToolEntry(
                name=name,
                toolset=toolset,
                schema=schema,
                handler=handler,
                check_fn=check_fn,
                description=description,
                emoji=emoji,
            )

    def get(self, name: str) -> Optional[ToolEntry]:
        return self._tools.get(name)

    def get_definitions(
        self,
        names: Optional[List[str]] = None,
        *,
        quiet_mode: bool = False,
    ) -> List[dict]:
        """组装发给模型的 OpenAI tools schema 列表。

        对照源码 ``registry.get_definitions``：只暴露 check_fn 通过的工具。
        """
        out: List[dict] = []
        with self._lock:
            entries = list(self._tools.values())
        for entry in entries:
            if names is not None and entry.name not in names:
                continue
            if entry.check_fn is not None:
                try:
                    if not entry.check_fn():
                        continue
                except Exception:
                    continue
            # OpenAI chat.completions tools 包装
            out.append({"type": "function", "function": dict(entry.schema)})
            if not quiet_mode:
                print(f"  [registry] expose tool={entry.name} toolset={entry.toolset}")
        return out

    def dispatch(self, name: str, args: dict, **kwargs: Any) -> str:
        """执行已注册 handler，必须返回 JSON 字符串。"""
        entry = self.get(name)
        if entry is None:
            return tool_error(f"Unknown tool: {name}")
        try:
            result = entry.handler(args if isinstance(args, dict) else {}, **kwargs)
        except Exception as exc:
            return tool_error(f"{name} failed: {exc}")
        if not isinstance(result, str):
            result = json.dumps(result, ensure_ascii=False)
        return result

    def names(self) -> List[str]:
        with self._lock:
            return sorted(self._tools.keys())


# 进程内单例（对照源码 ``registry = ToolRegistry()``）
registry = ToolRegistry()
