from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from .schema import validate_args
from .whitelist import ToolWhitelist


@dataclass
class AuditLog:
    entries: List[dict] = field(default_factory=list)

    def append(self, event: dict) -> None:
        self.entries.append(event)


def invoke_tool_layered(
    tool_name: str,
    args: dict,
    tools: Dict[str, Callable[..., Any]],
    whitelist: ToolWhitelist,
    audit: AuditLog,
) -> Any:
    """分层：白名单 → Schema 校验 → 执行 → 审计。"""
    whitelist.check(tool_name)
    validate_args(tool_name, args)
    audit.append({"event": "tool_invoke", "tool": tool_name, "args": args})
    return tools[tool_name](**args)
