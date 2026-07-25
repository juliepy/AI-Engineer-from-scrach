# =============================================================================
# Todo Tool — 对照 hermes_src/tools/todo_tool.py（精简保留核心路径）
# =============================================================================
# 保留：TodoStore / todo_tool / TODO_SCHEMA / registry.register
# 省略：超大 payload 防护常量细节以外的 gateway hydrate 旁路
# =============================================================================
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from registry import registry, tool_error

VALID_STATUSES = {"pending", "in_progress", "completed", "cancelled"}
MAX_TODO_CONTENT_CHARS = 4000
MAX_TODO_ITEMS = 256


class TodoStore:
    """In-memory todo list. One instance per AIAgent (one per session).

    Items are ordered — list position is priority. Each item has:
      - id: unique string identifier (agent-chosen)
      - content: task description
      - status: pending | in_progress | completed | cancelled
    """

    def __init__(self) -> None:
        self._items: List[Dict[str, str]] = []

    def has_items(self) -> bool:
        return bool(self._items)

    def read(self) -> List[Dict[str, str]]:
        return [dict(i) for i in self._items]

    def write(self, todos: List[Dict[str, Any]], merge: bool = False) -> List[Dict[str, str]]:
        if not merge:
            self._items = [self._validate(t) for t in self._dedupe_by_id(todos)]
        else:
            existing = {item["id"]: item for item in self._items}
            for t in self._dedupe_by_id(todos):
                item_id = str(t.get("id", "")).strip()
                if not item_id:
                    continue
                if item_id in existing:
                    if "content" in t and t["content"]:
                        existing[item_id]["content"] = self._cap_content(str(t["content"]).strip())
                    if "status" in t and t["status"]:
                        status = str(t["status"]).strip().lower()
                        if status in VALID_STATUSES:
                            existing[item_id]["status"] = status
                else:
                    validated = self._validate(t)
                    existing[validated["id"]] = validated
                    self._items.append(validated)
            seen = set()
            rebuilt = []
            for item in self._items:
                current = existing.get(item["id"], item)
                if current["id"] not in seen:
                    rebuilt.append(current)
                    seen.add(current["id"])
            self._items = rebuilt
        if len(self._items) > MAX_TODO_ITEMS:
            self._items = self._items[:MAX_TODO_ITEMS]
        return self.read()

    def _cap_content(self, content: str) -> str:
        if len(content) <= MAX_TODO_CONTENT_CHARS:
            return content
        return content[: MAX_TODO_CONTENT_CHARS - 1] + "…"

    def _validate(self, t: Dict[str, Any]) -> Dict[str, str]:
        item_id = str(t.get("id", "")).strip() or "item"
        content = self._cap_content(str(t.get("content", "")).strip())
        status = str(t.get("status", "pending")).strip().lower()
        if status not in VALID_STATUSES:
            status = "pending"
        return {"id": item_id, "content": content, "status": status}

    @staticmethod
    def _dedupe_by_id(todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for t in todos:
            tid = str(t.get("id", "")).strip()
            if not tid or tid in seen:
                continue
            seen.add(tid)
            out.append(t)
        return out


def todo_tool(
    todos: Optional[List[Dict[str, Any]]] = None,
    merge: bool = False,
    store: Optional[TodoStore] = None,
) -> str:
    """Single entry point. Provide todos to write; omit to read. Always returns full list."""
    if store is None:
        return tool_error("TodoStore not initialized")

    if todos is not None:
        if isinstance(todos, str):
            try:
                todos = json.loads(todos)
            except (json.JSONDecodeError, TypeError):
                return tool_error("todos must be a list of objects, got unparseable string")
        if not isinstance(todos, list):
            return tool_error(f"todos must be a list, got {type(todos).__name__}")
        items = store.write(todos, merge)
    else:
        items = store.read()

    pending = sum(1 for i in items if i["status"] == "pending")
    in_progress = sum(1 for i in items if i["status"] == "in_progress")
    completed = sum(1 for i in items if i["status"] == "completed")
    cancelled = sum(1 for i in items if i["status"] == "cancelled")

    return json.dumps(
        {
            "todos": items,
            "summary": {
                "total": len(items),
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed,
                "cancelled": cancelled,
            },
        },
        ensure_ascii=False,
    )


def check_todo_requirements() -> bool:
    return True


TODO_SCHEMA = {
    "name": "todo",
    "description": (
        "Manage your task list for the current session. Use for complex tasks "
        "with 3+ steps or when the user provides multiple tasks. "
        "Call with no parameters to read the current list.\n\n"
        "Writing:\n"
        "- Provide 'todos' array to create/update items\n"
        "- merge=false (default): replace the entire list with a fresh plan\n"
        "- merge=true: update existing items by id, add any new ones\n\n"
        "Each item: {id: string, content: string, "
        "status: pending|in_progress|completed|cancelled}\n"
        "List order is priority. Only ONE item in_progress at a time.\n"
        "Mark items completed immediately when done. If something fails, "
        "cancel it and add a revised item.\n\n"
        "Always returns the full current list."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "todos": {
                "type": "array",
                "description": "Task items to write. Omit to read current list.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique item identifier"},
                        "content": {"type": "string", "description": "Task description"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "Current status",
                        },
                    },
                    "required": ["id", "content", "status"],
                },
            },
            "merge": {
                "type": "boolean",
                "description": (
                    "true: update existing items by id, add new ones. "
                    "false (default): replace the entire list."
                ),
                "default": False,
            },
        },
        "required": [],
    },
}


# --- Registry（schema 可见；真正执行时常被 agent 级 invoke_tool 截胡）---
registry.register(
    name="todo",
    toolset="todo",
    schema=TODO_SCHEMA,
    handler=lambda args, **kw: todo_tool(
        todos=args.get("todos"),
        merge=args.get("merge", False),
        store=kw.get("store"),
    ),
    check_fn=check_todo_requirements,
    emoji="📋",
)
