"""把 02-run-agent/demo/exports/agent_loop/ 实跑导出解析成 scorer 用的 run dict。

需要目录内至少有：
  00_workflow.md · 04_messages.md · 05_final_response.md · 06_trace.md
可选：01_system.md（拼进 messages[0] 便于对照）
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_WORKFLOW_FIELD = re.compile(
    r"^-\s+(?P<key>[\w /]+):\s+`(?P<val>[^`]*)`\s*$",
    re.M,
)
_MSG_SPLIT = re.compile(r"^## \[(\d+)\] role=(\w+)\s*$", re.M)
_TRACE_SPLIT = re.compile(r"^## api#(\d+) · (\w+)\s*$", re.M)
_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.S)


def _parse_workflow(text: str) -> dict[str, Any]:
    fields: dict[str, str] = {}
    for m in _WORKFLOW_FIELD.finditer(text):
        fields[m.group("key").strip()] = m.group("val").strip()

    budget_used, budget_max = 0, 0
    bm = fields.get("budget used/max", "")
    if "/" in bm:
        a, b = bm.split("/", 1)
        budget_used, budget_max = int(a), int(b)

    tools_raw = fields.get("tools", "[]")
    try:
        tools = json.loads(tools_raw.replace("'", '"'))
    except json.JSONDecodeError:
        tools = []

    return {
        "model": fields.get("model"),
        "exit_reason": fields.get("exit_reason"),
        "api_calls": int(fields.get("api_calls") or 0),
        "budget_used": budget_used,
        "budget_max": budget_max,
        "tools_declared": tools,
    }


def _parse_messages(text: str) -> list[dict[str, Any]]:
    parts = _MSG_SPLIT.split(text)
    messages: list[dict[str, Any]] = []
    # parts: [preamble, idx, role, body, idx, role, body, ...]
    for i in range(1, len(parts), 3):
        role = parts[i + 1]
        body = parts[i + 2].strip()
        # 去掉尾部分隔 ---
        body = re.sub(r"\n---\s*$", "", body).strip()
        msg: dict[str, Any] = {"role": role, "content": body}

        if role == "tool":
            name_m = re.search(r"^-\s*name:\s*`([^`]+)`", body, re.M)
            id_m = re.search(r"^-\s*tool_call_id:\s*`([^`]+)`", body, re.M)
            if name_m:
                msg["name"] = name_m.group(1)
            if id_m:
                msg["tool_call_id"] = id_m.group(1)
            # content：去掉元数据行
            content_lines = [
                ln
                for ln in body.splitlines()
                if not re.match(r"^-\s*(tool_call_id|name):", ln)
            ]
            msg["content"] = "\n".join(content_lines).strip()

        if role == "assistant":
            blocks = _JSON_BLOCK.findall(body)
            if blocks:
                try:
                    tc = json.loads(blocks[0])
                    if isinstance(tc, list):
                        msg["tool_calls"] = tc
                        # 正文去掉 json 块
                        msg["content"] = _JSON_BLOCK.sub("", body).strip()
                        if msg["content"] in {"*(empty content)*", ""}:
                            msg["content"] = ""
                except json.JSONDecodeError:
                    pass
            if msg.get("content") == "*(empty content)*":
                msg["content"] = ""

        messages.append(msg)
    return messages


def _parse_trace(text: str) -> list[dict[str, Any]]:
    parts = _TRACE_SPLIT.split(text)
    events: list[dict[str, Any]] = []
    for i in range(1, len(parts), 3):
        api_call = int(parts[i])
        kind = parts[i + 1]
        body = parts[i + 2]
        blocks = _JSON_BLOCK.findall(body)
        detail: dict[str, Any] = {}
        if blocks:
            try:
                detail = json.loads(blocks[0])
            except json.JSONDecodeError:
                detail = {"raw": blocks[0][:500]}
        ev: dict[str, Any] = {"api_call": api_call, "kind": kind, **detail}
        # 从 message_roles 推导 system_fingerprint（实跑 trace 通常无该字段）
        if kind == "api_request" and "system_fingerprint" not in ev:
            roles = detail.get("message_roles") or []
            sys_chars = next(
                (r.get("chars") for r in roles if r.get("role") == "system"),
                None,
            )
            if sys_chars is not None:
                ev["system_fingerprint"] = f"chars:{sys_chars}"
        if kind == "loop_exit":
            # loop_exit JSON 用 reason；对齐 scorer 的 exit_reason 已在 workflow
            pass
        events.append(ev)
    return events


def load_agent_loop_export(export_dir: Path) -> dict[str, Any]:
    """解析 02 demo 导出目录 → run dict。"""
    export_dir = export_dir.resolve()
    workflow_path = export_dir / "00_workflow.md"
    messages_path = export_dir / "04_messages.md"
    final_path = export_dir / "05_final_response.md"
    trace_path = export_dir / "06_trace.md"
    system_path = export_dir / "01_system.md"

    for p in (workflow_path, messages_path, final_path, trace_path):
        if not p.exists():
            raise FileNotFoundError(f"02 export missing {p.name} under {export_dir}")

    meta = _parse_workflow(workflow_path.read_text(encoding="utf-8"))
    messages = _parse_messages(messages_path.read_text(encoding="utf-8"))
    if system_path.exists():
        system = system_path.read_text(encoding="utf-8").strip()
        if not messages or messages[0].get("role") != "system":
            messages = [{"role": "system", "content": system}, *messages]

    final_response = final_path.read_text(encoding="utf-8")
    trace = _parse_trace(trace_path.read_text(encoding="utf-8"))

    # loop_exit 可校正 exit_reason / budget
    for ev in reversed(trace):
        if ev.get("kind") == "loop_exit":
            meta["exit_reason"] = ev.get("reason") or meta.get("exit_reason")
            if "budget_used" in ev:
                meta["budget_used"] = int(ev["budget_used"])
            if "budget_max" in ev:
                meta["budget_max"] = int(ev["budget_max"])
            break

    return {
        "id": f"from_02:{export_dir.name}",
        "source": str(export_dir),
        "model": meta.get("model"),
        "exit_reason": meta.get("exit_reason"),
        "api_calls": meta.get("api_calls", 0),
        "budget_used": meta.get("budget_used", 0),
        "budget_max": meta.get("budget_max", 0),
        "final_response": final_response,
        "messages": messages,
        "trace": trace,
    }


def is_agent_loop_export_dir(path: Path) -> bool:
    return path.is_dir() and (path / "06_trace.md").exists() and (path / "00_workflow.md").exists()
