# =============================================================================
# 教学版 conversation_loop.run_conversation
# 对照源码: hermes_src/agent/conversation_loop.py（while ~:645）
#           hermes_src/run_agent.py · run_conversation forwarder
# =============================================================================
# 保留：while 条件（iterations / budget / grace）+ interrupt + API + tool 分支
# 省略：压缩、重试、Codex、guardrail、stream TTS、plugin hooks、DB persist…
# =============================================================================
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from invoke_tool import invoke_tool
from iteration_budget import IterationBudget


@dataclass
class LoopTraceEvent:
    """教学扩展：记录每一步 API / tool，方便 exports 可视化。"""

    kind: str  # api_request | api_response | tool_result | loop_exit
    api_call: int = 0
    detail: Dict[str, Any] = field(default_factory=dict)


def _safe_print(agent: Any, text: str) -> None:
    printer = getattr(agent, "_safe_print", None)
    if callable(printer):
        printer(text)
    else:
        print(text)


def _append_assistant_with_tools(messages: list, assistant_message: Any) -> dict:
    """把 SDK assistant message（含 tool_calls）写成 OpenAI messages 格式。"""
    tool_calls_payload = []
    for tc in assistant_message.tool_calls or []:
        tool_calls_payload.append(
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                    if isinstance(tc.function.arguments, str)
                    else json.dumps(tc.function.arguments or {}),
                },
            }
        )
    msg = {
        "role": "assistant",
        "content": assistant_message.content or "",
        "tool_calls": tool_calls_payload,
    }
    messages.append(msg)
    return msg


def _execute_tool_calls_sequential(
    agent: Any,
    assistant_message: Any,
    messages: list,
    effective_task_id: str,
    api_call_count: int,
    trace: List[LoopTraceEvent],
) -> None:
    """对照 ``_execute_tool_calls_sequential``：逐个 invoke → append role=tool。"""
    for tc in assistant_message.tool_calls or []:
        name = tc.function.name
        raw_args = tc.function.arguments
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args) if raw_args.strip() else {}
            except json.JSONDecodeError:
                args = {}
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            args = {}

        _safe_print(agent, f"  ┊ tool → {name}({json.dumps(args, ensure_ascii=False)[:120]})")
        # agent 级截胡（todo）或 registry.dispatch（calculator）
        result = invoke_tool(
            agent,
            name,
            args,
            effective_task_id=effective_task_id,
            tool_call_id=tc.id,
            messages=messages,
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": result,
            }
        )
        trace.append(
            LoopTraceEvent(
                kind="tool_result",
                api_call=api_call_count,
                detail={"name": name, "args": args, "result": result},
            )
        )
        _safe_print(agent, f"  ┊ result ← {result[:200]}")


def run_conversation(
    agent: Any,
    user_message: str,
    system_message: str = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    task_id: str = None,
) -> Dict[str, Any]:
    """Run a complete conversation with tool calling until completion.

    对照源码签名 / 返回值结构；主路径是同步 while。
    """
    # ── Per-turn setup（源码里大量 prologue；demo 只做最小拼装）──────────
    effective_task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
    agent.iteration_budget = IterationBudget(agent.max_iterations)
    agent._budget_grace_call = False
    agent._interrupt_requested = False

    messages: List[Dict[str, Any]] = list(conversation_history or [])
    messages.append({"role": "user", "content": user_message})

    active_system_prompt = system_message or agent._cached_system_prompt or ""
    tools = agent.tools  # OpenAI tools schema list
    valid_names = set(agent.valid_tool_names or [])

    chat_with_tools: Callable = agent._chat_with_tools
    if not callable(chat_with_tools):
        raise RuntimeError("DemoAgent missing _chat_with_tools")

    api_call_count = 0
    final_response = None
    interrupted = False
    _turn_exit_reason = "unknown"
    trace: List[LoopTraceEvent] = []

    _safe_print(
        agent,
        f"\n▶ enter while  max_iterations={agent.max_iterations} "
        f"budget.remaining={agent.iteration_budget.remaining}",
    )

    # ── ★ 主循环骨架（与 AGENTS.md / conversation_loop while 对齐）──────
    while (
        api_call_count < agent.max_iterations and agent.iteration_budget.remaining > 0
    ) or agent._budget_grace_call:

        if agent._interrupt_requested:
            interrupted = True
            _turn_exit_reason = "interrupted_by_user"
            _safe_print(agent, "\n⚡ Breaking out of tool loop due to interrupt...")
            break

        api_call_count += 1
        agent._api_call_count = api_call_count

        # Grace call: 预算用尽后再给一次收尾机会
        if agent._budget_grace_call:
            agent._budget_grace_call = False
            _safe_print(agent, f"  · grace call #{api_call_count}")
        elif not agent.iteration_budget.consume():
            _turn_exit_reason = "budget_exhausted"
            _safe_print(
                agent,
                f"\n⚠️  Iteration budget exhausted "
                f"({agent.iteration_budget.used}/{agent.iteration_budget.max_total})",
            )
            break

        _safe_print(
            agent,
            f"\n── API call #{api_call_count}  "
            f"budget used={agent.iteration_budget.used} "
            f"remaining={agent.iteration_budget.remaining} ──",
        )

        # 组装请求（教学：把 system + messages + tools 完整记进 trace）
        api_messages = [{"role": "system", "content": active_system_prompt}] + [
            {k: v for k, v in m.items() if k != "_meta"} for m in messages
        ]
        trace.append(
            LoopTraceEvent(
                kind="api_request",
                api_call=api_call_count,
                detail={
                    "messages": api_messages,
                    "tool_names": sorted(valid_names),
                },
            )
        )

        assistant_message = chat_with_tools(
            system=active_system_prompt,
            messages=messages,
            tools=tools,
        )

        content_preview = (assistant_message.content or "")[:120]
        tc_names = [tc.function.name for tc in (assistant_message.tool_calls or [])]
        trace.append(
            LoopTraceEvent(
                kind="api_response",
                api_call=api_call_count,
                detail={
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                        for tc in (assistant_message.tool_calls or [])
                    ],
                },
            )
        )
        _safe_print(
            agent,
            f"  ← assistant content={content_preview!r} tool_calls={tc_names}",
        )

        # Check for tool calls
        if assistant_message.tool_calls:
            # 校验名字（源码会 repair / 回错误给模型；demo 简化）
            invalid = [
                tc.function.name
                for tc in assistant_message.tool_calls
                if tc.function.name not in valid_names
            ]
            if invalid:
                _append_assistant_with_tools(messages, assistant_message)
                available = ", ".join(sorted(valid_names))
                for tc in assistant_message.tool_calls:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": tc.function.name,
                            "content": (
                                f"Tool '{tc.function.name}' does not exist. "
                                f"Available tools: {available}"
                                if tc.function.name not in valid_names
                                else "Skipped: another tool call used an invalid name."
                            ),
                        }
                    )
                continue

            _append_assistant_with_tools(messages, assistant_message)
            # 对照 conversation_loop ~:3430
            _execute_tool_calls_sequential(
                agent,
                assistant_message,
                messages,
                effective_task_id,
                api_call_count,
                trace,
            )
            # Continue loop for next response
            continue

        # No tool calls — final response
        final_response = assistant_message.content or ""
        messages.append({"role": "assistant", "content": final_response})
        _turn_exit_reason = "completed"
        break
    else:
        if final_response is None:
            _turn_exit_reason = "max_iterations"

    # ── Grace call（教学演示）：预算/轮次耗尽但仍停在 tool 结果上时，
    # 再给模型一次「只能出文字」的收尾机会（对照 _budget_grace_call）。
    if final_response is None and not interrupted and messages:
        last = messages[-1]
        if last.get("role") == "tool":
            agent._budget_grace_call = True
            _safe_print(
                agent,
                "\n✦ budget/iterations exhausted after tools → grace call "
                "(no tools, force final text)",
            )
            api_call_count += 1
            assistant_message = chat_with_tools(
                system=active_system_prompt
                + "\n\n[SYSTEM] Iteration budget exhausted. "
                "Do NOT call tools. Write the final Chinese answer now "
                "using conversation history and tool results already above.",
                messages=messages,
                tools=None,
                tool_choice=None,
            )
            final_response = assistant_message.content or ""
            messages.append({"role": "assistant", "content": final_response})
            _turn_exit_reason = "budget_grace_call"
            trace.append(
                LoopTraceEvent(
                    kind="api_response",
                    api_call=api_call_count,
                    detail={
                        "content": final_response,
                        "tool_calls": [],
                        "grace": True,
                    },
                )
            )

    if final_response is None and not interrupted:
        final_response = (
            f"(no final text; exit={_turn_exit_reason}; "
            f"api_calls={api_call_count})"
        )

    trace.append(
        LoopTraceEvent(
            kind="loop_exit",
            api_call=api_call_count,
            detail={
                "reason": _turn_exit_reason,
                "interrupted": interrupted,
                "budget_used": agent.iteration_budget.used,
                "budget_max": agent.iteration_budget.max_total,
            },
        )
    )
    _safe_print(
        agent,
        f"\n■ exit reason={_turn_exit_reason} api_calls={api_call_count} "
        f"budget={agent.iteration_budget.used}/{agent.iteration_budget.max_total}",
    )

    agent._loop_trace = trace
    completed = _turn_exit_reason in {"completed", "budget_grace_call"} and bool(
        final_response
    ) and not str(final_response).startswith("(no final text")
    return {
        "final_response": final_response,
        "messages": messages,
        "api_calls": api_call_count,
        "completed": completed,
        "partial": not completed,
        "exit_reason": _turn_exit_reason,
        "trace": trace,
    }
