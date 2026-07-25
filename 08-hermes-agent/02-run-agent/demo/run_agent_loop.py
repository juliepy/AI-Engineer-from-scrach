#!/usr/bin/env python3
# =============================================================================
# Agent Loop Demo — 可跑通的「思考 → 工具 → 观察 → 再思考」
# =============================================================================
# 对照讲稿: notes/1_agent_loop.md · notes/2_tools_discovery.md · notes/3_todo_intercept.md
# 对照源码: hermes_src/agent/conversation_loop.py（while）
#           hermes_src/tools/todo_tool.py · web_tools.py（schema/返回形）
#           01-memory：MEMORY/USER 冻进 system；conversation_history fixture
#
# 跑法:
#   cd 02-run-agent/demo
#   pip install -r requirements.txt
#   # DEEPSEEK_API_KEY=sk-...  （可选 TAVILY_API_KEY；否则用 ddgs）
#   python run_agent_loop.py
# =============================================================================
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# teaching/ 按讲稿拆成子目录；全部入 path，模块间仍用扁平 import
for _subdir in ("agent_loop", "tools", "todo", "memory"):
    sys.path.insert(0, str(HERE / "teaching" / _subdir))

from agent import DemoAgent
from llm import DEEPSEEK_MODEL, format_tools_brief, make_chat_with_tools, require_api_key
from teaching_memory import TeachingMemoryStore
from web_search_tool import active_backend_name

FIXTURES = HERE / "fixtures"
FIXTURE_CONV = FIXTURES / "conversation_history.md"
FIXTURE_MEMORY = FIXTURES / "MEMORY.md"
FIXTURE_USER = FIXTURES / "USER.md"
EXPORT_DIR = HERE / "exports" / "agent_loop"

# 拼在 MEMORY/USER 后面：告诉模型本 demo 可用的工具（对照 core tool schema 行为指引）
TOOLS_GUIDANCE = """
You have these tools for this session:
- `todo`: session task list (agent-level state). Use for multi-step work.
- `web_search`: search the web; returns titles/URLs/descriptions (JSON).

Workflow for this turn (STRICT):
1. Call `todo` once to write a short plan (2-3 items).
2. Call `web_search` **at most twice total** (prefer one precise query).
   Good queries: site:hermes-agent.nousresearch.com agent loop
                site:github.com/NousResearch/hermes-agent conversation_loop
3. Call `todo` with merge=true to mark items completed.
4. Stop searching. Reply in Chinese with an interview-ready summary grounded
   in prior conversation history AND the search hits you already have.
   Cite at least one title/URL from web_search results.

Do not invent search results. Do not keep searching after you already have
official docs / GitHub / DeepWiki hits.
""".strip()


def banner(step: str, title: str) -> None:
    print()
    print("=" * 72)
    print(f"  STEP {step} · {title}")
    print("=" * 72)


def dump(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(HERE)}")


def load_conversation_history(path: Path) -> list[dict]:
    """把 conversation_history.md 拆成消息列表（对齐 01-memory demo）。

    丢掉内嵌 system —— 真正的 system 由 TeachingMemoryStore 冻进缓存。
    """
    raw = path.read_text(encoding="utf-8")
    parts = re.split(r"^===== \[(\d+)\] role=(\w+) =====\s*$", raw, flags=re.M)
    messages: list[dict] = []
    for i in range(1, len(parts), 3):
        role = parts[i + 1]
        body = parts[i + 2].strip()
        messages.append({"role": role, "content": body})
    if not messages:
        raise ValueError(f"空对话 fixture: {path}")
    return [m for m in messages if m["role"] != "system"]


def format_messages_md(messages: list[dict], *, title: str) -> str:
    lines = [f"# {title}", ""]
    for i, m in enumerate(messages):
        role = m.get("role")
        content = m.get("content") or ""
        lines.append(f"## [{i}] role={role}")
        if m.get("tool_calls"):
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(m["tool_calls"], ensure_ascii=False, indent=2))
            lines.append("```")
        if role == "tool":
            lines.append(f"- tool_call_id: `{m.get('tool_call_id')}`")
            lines.append(f"- name: `{m.get('name')}`")
        lines.append("")
        lines.append(content if content else "*(empty content)*")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def format_trace_md(trace: list) -> str:
    lines = ["# Agent Loop Trace", ""]
    for ev in trace:
        lines.append(f"## api#{ev.api_call} · {ev.kind}")
        lines.append("")
        # api_request 的 messages 很长：只保留 roles 摘要
        detail = ev.detail
        if ev.kind == "api_request" and isinstance(detail.get("messages"), list):
            detail = {
                "tool_names": detail.get("tool_names"),
                "message_roles": [
                    {
                        "i": i,
                        "role": m.get("role"),
                        "chars": len(m.get("content") or ""),
                        "tool_calls": bool(m.get("tool_calls")),
                    }
                    for i, m in enumerate(detail["messages"])
                ],
            }
        lines.append("```json")
        lines.append(json.dumps(detail, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def role_timeline(messages: list[dict]) -> str:
    rows = []
    for i, m in enumerate(messages):
        role = m.get("role")
        extra = ""
        if m.get("tool_calls"):
            names = [tc["function"]["name"] for tc in m["tool_calls"]]
            extra = f" tool_calls={names}"
        elif role == "tool":
            extra = f" name={m.get('name')}"
        rows.append(f"  [{i}] {role}{extra}")
    return "\n".join(rows)


def main() -> int:
    # 本 turn 的用户消息（接着 fixtures/conversation_history.md）
    user_prompt = (
        "接着前面聊的主循环：先 todo 写计划，再 web_search 最多两次 "
        "（优先 site:hermes-agent.nousresearch.com agent loop 或 "
        "site:github.com/NousResearch/hermes-agent conversation_loop），"
        "核对三个刹车 + todo 截胡。搜到官方文档/GitHub 后立刻结束搜索、"
        "todo 标完成，用中文给面试话术，并引用至少一条结果的标题或 URL。"
        "禁止反复换关键词空转搜索。"
    )

    api_key = require_api_key()
    print(f"[mode] DeepSeek live ({DEEPSEEK_MODEL}, key len={len(api_key)})")
    print(f"[web]  search backend = {active_backend_name()}")

    # ── STEP 1: load MEMORY / USER / conversation_history（对齐 01-memory）─
    banner("1", "Load fixtures → MEMORY+USER → system；history → conversation_history")
    for p in (FIXTURE_CONV, FIXTURE_MEMORY, FIXTURE_USER):
        if not p.exists():
            print(f"缺少 fixture: {p}")
            return 1

    store = TeachingMemoryStore(memory_dir=FIXTURES)
    store.load_from_disk()
    system_prompt = store.build_system_prompt(
        role_line=(
            "你是编程助手 Hermes。回答要具体、能对着源码讲；"
            "涉及面试时给出可直接用的话术。"
        )
    )
    system_prompt = system_prompt + "\n\n" + TOOLS_GUIDANCE
    history = load_conversation_history(FIXTURE_CONV)
    print(f"  MEMORY entries: {len(store.memory_entries)}")
    print(f"  USER entries:   {len(store.user_entries)}")
    print(f"  history msgs:   {len(history)} (system rows dropped)")
    print(f"  system chars:   {len(system_prompt)}")

    # ── STEP 2: wire tools + agent ───────────────────────────────────────
    banner("2", "Registry expose tools → DemoAgent")
    chat_with_tools = make_chat_with_tools(api_key)
    agent = DemoAgent(
        chat_with_tools=chat_with_tools,
        system_prompt=system_prompt,
        enabled_tools=["todo", "web_search"],
        max_iterations=6,
        model=DEEPSEEK_MODEL,
    )
    print("\nExposed tools:")
    print(format_tools_brief(agent.tools))
    print(f"\nvalid_tool_names = {sorted(agent.valid_tool_names)}")
    print("todo:       agent-level intercept → agent._todo_store")
    print(f"web_search: registry.dispatch    → backend={active_backend_name()}")

    # ── STEP 3: run_conversation while loop ──────────────────────────────
    banner("3", "run_conversation — history + while 思考→工具→观察")
    print(
        """
  workflow:
    MEMORY.md + USER.md → frozen system_prompt (prompt cache prefix)
    conversation_history.md → prior user/assistant turns
    append current user
      → while (api_call_count < max and budget.remaining > 0) or grace:
           DeepSeek(+ tools) → tool_calls? invoke → continue : final
"""
    )
    result = agent.run_conversation(
        user_message=user_prompt,
        system_message=system_prompt,
        conversation_history=history,
        task_id="demo-agent-loop",
    )

    # ── STEP 4: 打印时序与最终回复 ───────────────────────────────────────
    banner("4", "Role timeline + final_response")
    print("\n----- ROLE TIMELINE -----\n")
    print(role_timeline(result["messages"]))
    print("\n----- FINAL RESPONSE -----\n")
    print(result.get("final_response") or "")
    print("\n----- TODO STORE (agent-level state) -----\n")
    print(json.dumps(agent._todo_store.read(), ensure_ascii=False, indent=2))
    print(
        f"\nexit_reason={result.get('exit_reason')} "
        f"api_calls={result.get('api_calls')} "
        f"completed={result.get('completed')}"
    )

    # ── STEP 5: export ───────────────────────────────────────────────────
    banner("5", "Export → demo/exports/agent_loop/")
    dump(
        EXPORT_DIR / "00_workflow.md",
        f"""# Agent Loop Workflow

```text
fixtures/
  MEMORY.md + USER.md  → TeachingMemoryStore → frozen system (+ tools guidance)
  conversation_history.md → prior turns (no system row)

DemoAgent.run_conversation(user, history, system)
        │
        ▼
conversation_loop.run_conversation
        ├─ messages = history + current user
        ├─ IterationBudget(max_iterations={agent.max_iterations})
        └─ while …:
              DeepSeek(+ todo, web_search)
              tool_calls? → invoke_tool → role=tool → continue
              text? → final_response
```

- model: `{DEEPSEEK_MODEL}`
- web backend: `{active_backend_name()}`
- exit_reason: `{result.get('exit_reason')}`
- api_calls: `{result.get('api_calls')}`
- budget used/max: `{agent.iteration_budget.used}/{agent.iteration_budget.max_total}`
- tools: `{sorted(agent.valid_tool_names)}`
- history_before_turn: `{len(history)}`
- memory/user entries: `{len(store.memory_entries)}` / `{len(store.user_entries)}`

## Role timeline

```text
{role_timeline(result['messages'])}
```
""",
    )
    dump(
        EXPORT_DIR / "00_memory_block.md",
        store.format_for_system_prompt("memory") or "(empty)",
    )
    dump(
        EXPORT_DIR / "00_user_block.md",
        store.format_for_system_prompt("user") or "(empty)",
    )
    dump(EXPORT_DIR / "01_system.md", system_prompt)
    dump(EXPORT_DIR / "02_user.md", user_prompt)
    dump(
        EXPORT_DIR / "02_history.md",
        format_messages_md(history, title="conversation_history (before this turn)"),
    )
    dump(
        EXPORT_DIR / "03_tools_schema.json",
        json.dumps(agent.tools, ensure_ascii=False, indent=2),
    )
    dump(
        EXPORT_DIR / "04_messages.md",
        format_messages_md(result["messages"], title="Full messages after loop"),
    )
    dump(EXPORT_DIR / "05_final_response.md", result.get("final_response") or "")
    dump(EXPORT_DIR / "06_trace.md", format_trace_md(result.get("trace") or []))
    dump(
        EXPORT_DIR / "07_todo_store.json",
        json.dumps(agent._todo_store.read(), ensure_ascii=False, indent=2),
    )

    banner("done", "Agent loop demo finished")
    print(
        f"""
查看产物:
  {EXPORT_DIR.relative_to(HERE)}/

Fixtures:
  fixtures/MEMORY.md
  fixtures/USER.md
  fixtures/conversation_history.md

对照:
  ../hermes_src/tools/todo_tool.py
  teaching/todo/todo_tool.py
  teaching/tools/web_search_tool.py  ← web_tools.py schema/返回形
  ../../01-memory/demo/        ← MEMORY/USER + history 加载方式
"""
    )
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
