from typing import Set


class ToolWhitelist:
    def __init__(self, allowed: Set[str]):
        self.allowed = allowed

    def check(self, tool_name: str) -> None:
        if tool_name not in self.allowed:
            raise PermissionError(f"tool '{tool_name}' not in whitelist")
