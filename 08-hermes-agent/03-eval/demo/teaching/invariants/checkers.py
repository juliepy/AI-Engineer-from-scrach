"""Agent-loop 行为不变量（教学版）。

对照：hermes_src/AGENTS.md「Don't write change-detector tests」
     hermes_src/tests/agent/test_prompt_caching.py（契约风格）
"""
from __future__ import annotations

from typing import Any


def check_role_alternation(messages: list[dict[str, Any]]) -> tuple[bool, str]:
    """消息 role 契约。

    允许：
    - 同轮多条 `tool`
    - 连续 `user`（history 以 user 收尾 + 本 turn 再 append user，02 实跑常见）

    不允许：
    - 连续 `assistant` / `system`
    """
    prev: str | None = None
    for i, m in enumerate(messages):
        role = m.get("role")
        if role is None:
            return False, f"messages[{i}] missing role"
        if prev is None:
            prev = role
            continue
        if role == prev and role not in {"tool", "user"}:
            return False, f"messages[{i}]: consecutive role={role!r} (prev also {prev!r})"
        prev = role
    return True, "ok"


def check_system_stable(trace: list[dict[str, Any]]) -> tuple[bool, str]:
    """同 turn 内各次 api_request 的 system 指纹应一致（保 prompt cache）。

    教学 fixture 用 system_fingerprint 字段；没有则从 message_roles 推断。
    """
    fingerprints: list[str] = []
    for ev in trace:
        if ev.get("kind") != "api_request":
            continue
        fp = ev.get("system_fingerprint")
        if fp is None:
            roles = ev.get("message_roles") or []
            sys_chars = next((r.get("chars") for r in roles if r.get("role") == "system"), None)
            fp = f"chars:{sys_chars}" if sys_chars is not None else ""
        if fp:
            fingerprints.append(str(fp))
    if len(fingerprints) <= 1:
        return True, "single-or-empty request"
    first = fingerprints[0]
    for i, fp in enumerate(fingerprints[1:], start=2):
        if fp != first:
            return False, f"api#{i} system fingerprint {fp!r} != {first!r}"
    return True, f"stable across {len(fingerprints)} api_requests"


def check_tools_frozen(trace: list[dict[str, Any]]) -> tuple[bool, str]:
    """循环内 tools schema 集合不应中途增减。"""
    sets: list[frozenset[str]] = []
    for ev in trace:
        if ev.get("kind") != "api_request":
            continue
        names = ev.get("tool_names")
        if names is None:
            continue
        sets.append(frozenset(names))
    if len(sets) <= 1:
        return True, "single-or-empty"
    first = sets[0]
    for i, s in enumerate(sets[1:], start=2):
        if s != first:
            return False, f"api#{i} tools {sorted(s)} != {sorted(first)}"
    return True, f"frozen {sorted(first)}"


def check_budget_consistent(run: dict[str, Any]) -> tuple[bool, str]:
    used = int(run.get("budget_used", 0))
    maximum = int(run.get("budget_max", 0))
    api_calls = int(run.get("api_calls", 0))
    reason = run.get("exit_reason")
    if used > maximum:
        return False, f"budget_used {used} > budget_max {maximum}"
    if reason == "budget_grace_call" and api_calls != maximum + 1:
        return False, f"grace expects api_calls==budget_max+1, got {api_calls}"
    if reason == "budget_exhausted" and used < maximum:
        return False, f"exhausted but budget_used {used} < max {maximum}"
    return True, "ok"


# --- 故意写成「变更检测」的反例（教学对比，不要在真测试里用）---

CHANGE_DETECTOR_ANTI_PATTERNS = [
    'assert exit_reason == "budget_grace_call"  # 冻结某次实跑结果',
    'assert api_calls == 7  # 换模型/换 prompt 就会漂',
    'assert tool_sequence == ["todo", "web_search", ...]  # 精确序列快照',
]
