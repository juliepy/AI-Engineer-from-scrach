#!/usr/bin/env python3
# =============================================================================
# Turn Context Demo — 可跑通的单 turn prologue
# =============================================================================
# 对照讲稿: notebooks/5_compress.md
# 对照源码: hermes_src/agent/turn_context.py
#           hermes_src/agent/context_compressor.py
#           hermes_src/agent/conversation_compression.py
#
# 跑法:
#   cd 01-memory/demo
#   pip install -r ../notebooks/requirements.txt
#   # 在 demo/.env 写入 DEEPSEEK_API_KEY=sk-...
#   python run_turn_context.py
# =============================================================================
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "teaching"))

from llm import DEEPSEEK_MODEL, make_llm, require_api_key
from teaching_compressor import TeachingContextCompressor
from teaching_memory import TeachingMemoryStore
from teaching_turn_context import DemoAgent, build_turn_context


FIXTURES = HERE / "fixtures"
FIXTURE_CONV = FIXTURES / "long_conversation.md"
FIXTURE_MEMORY = FIXTURES / "MEMORY.md"
FIXTURE_USER = FIXTURES / "USER.md"
EXPORT_DIR = HERE / "exports" / "turn_context"


def banner(step: str, title: str) -> None:
    """在终端打一个醒目的步骤分隔条，方便跟着 demo 步骤看。"""
    print()
    print("=" * 72)
    print(f"  STEP {step} · {title}")
    print("=" * 72)


def dump(path: Path, text: str) -> None:
    """把一段文本写到 exports 目录（没有父目录就先建好）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(HERE)}")


def load_conversation_history(path: Path) -> list[dict]:
    """把 long_conversation.md 拆成消息列表。

    文件里按「===== [序号] role=xxx =====」分段。
    丢掉内嵌的短 system 行——真正的 system 由 TeachingMemoryStore 冻进缓存。
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
    # system 改由 TeachingMemoryStore 冻进 cached prompt
    return [m for m in messages if m["role"] != "system"]


class FixtureMemoryManager:
    """假的 memory_manager：用 MEMORY/USER 文件内容喂压缩与 prefetch 钩子。"""

    def __init__(self, store: TeachingMemoryStore):
        """记住底层的 TeachingMemoryStore，压缩时从它取身份提示。"""
        self.store = store

    def on_turn_start(self, turn_count: int, message: str) -> None:
        """每轮开始时的钩子（真源码里会做更多同步；demo 空实现即可）。"""
        pass

    def prefetch_all(self, query: str) -> str:
        """外部记忆预取：demo 里返回固定几句「相关提示」。

        权威用户画像仍在 system 的 USER/MEMORY 块里，这里只演示钩子还能附带内容。
        """
        return (
            "[ext-memory prefetch]\n"
            "- Prefer source-level Hermes explanations\n"
            "- Current focus: turn_context preflight compression"
        )

    def on_pre_compress(self, messages: list) -> str:
        """压缩前给 summarizer 一段身份提示，避免摘要把「我是谁」忘掉。"""
        return self.store.identity_hint_for_compress()


def format_messages_md(messages: list[dict], *, title: str) -> str:
    """把消息列表格式化成可读的 Markdown，方便写进 exports。"""
    lines = [f"# {title}", ""]
    for i, m in enumerate(messages):
        role = m.get("role")
        content = m.get("content") or ""
        lines.append(f"## [{i}] role={role}  ({len(content)} chars)")
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    """入口：装 memory → 压上下文 → 调主模型 → 把各步产物写到 exports。"""
    # 本 turn 的用户消息（改这里即可，不用命令行参数）
    user_prompt = (
        "请用 turn_context 的视角总结：preflight 什么时候触发压缩？"
        "压缩后发给主模型的 messages 长什么样？"
    )

    api_key = require_api_key()
    print(f"[mode] DeepSeek live ({DEEPSEEK_MODEL}, key len={len(api_key)})")

    # ── STEP 1: load MEMORY / USER / long_conversation ─────────────────────
    banner("1", "Load fixtures → MEMORY + USER → system_prompt；long_conversation → history")
    for p in (FIXTURE_CONV, FIXTURE_MEMORY, FIXTURE_USER):
        if not p.exists():
            print(f"缺少 fixture: {p}")
            return 1

    store = TeachingMemoryStore(memory_dir=FIXTURES)
    store.load_from_disk()
    system_prompt = store.build_system_prompt()
    history = load_conversation_history(FIXTURE_CONV)

    # ── STEP 2: wire agent + compressor ────────────────────────────────────
    banner("2", "Wire DemoAgent + TeachingContextCompressor + MemoryStore")
    summarize_fn, main_chat_fn = make_llm(api_key)
    # context_length 故意设小，让 fixture 必触发压缩（教学）
    compressor = TeachingContextCompressor(
        summarize_fn=summarize_fn,
        threshold_percent=0.50,
        protect_first_n=1,
        protect_last_n=2,
        context_length=600,
    )
    agent = DemoAgent(
        context_compressor=compressor,
        system_prompt=system_prompt,
        memory_manager=FixtureMemoryManager(store),
    )

    # ── STEP 3: build_turn_context（核心）─────────────────────────────────
    banner("3", "build_turn_context — prologue（含 preflight 压缩）")
    print(
        """
  workflow（对齐 turn_context.py）:
    append user message
      → load cached system prompt
      → cheap preflight gate
      → estimate tokens
      → should_compress?
      → agent._compress_context → TeachingContextCompressor
           → 切开 head/middle/tail
           → 辅助 LLM 摘要（DeepSeek）
           → SUMMARY_PREFIX 拼回
      → memory prefetch
      → return TurnContext
"""
    )
    ctx = build_turn_context(
        agent,
        user_message=user_prompt,
        system_message=system_prompt,
        conversation_history=history,
        task_id="demo-turn",
    )

    # ── STEP 4: 打印辅助模型 prompt / response ────────────────────────────
    banner("4", "辅助模型（compression）· prompt & response")
    if ctx.compression_ran:
        print("\n----- AUX PROMPT (发给摘要模型) -----\n")
        print(ctx.summarizer_prompt)
        print("\n----- AUX RESPONSE (摘要正文) -----\n")
        print(ctx.summarizer_response)
    else:
        print("本 turn 未触发压缩（可把 context_length 调更小）。")

    # ── STEP 5: 组装主模型请求并调用 ──────────────────────────────────────
    banner("5", "主模型 · 组装 prompt 并调用")
    # 若有 prefetch，真链路会注入 user 侧 context；这里演示拼到最新 user 后面
    messages_for_main = list(ctx.messages)
    if ctx.ext_prefetch_cache:
        # 找到最新「真」user（非 SUMMARY_PREFIX）并追加 prefetch 块
        for i in range(len(messages_for_main) - 1, -1, -1):
            m = messages_for_main[i]
            if m.get("role") != "user":
                continue
            c = m.get("content") or ""
            if "CONTEXT COMPACTION" in c:
                continue
            messages_for_main[i] = {
                **m,
                "content": (
                    c
                    + "\n\n---\n"
                    + ctx.ext_prefetch_cache
                ),
            }
            break

    print("\n----- MAIN SYSTEM PROMPT -----\n")
    print(ctx.active_system_prompt or "")
    print("\n----- MAIN MESSAGES (roles / sizes) -----\n")
    for i, m in enumerate(messages_for_main):
        c = m.get("content") or ""
        flag = ""
        if m.get("_compressed_summary") or "CONTEXT COMPACTION" in c:
            flag = "  ← SUMMARY"
        print(f"  [{i}] {m.get('role'):9s}  {len(c):5d} chars{flag}")

    print("\n----- MAIN RESPONSE -----\n")
    main_response = main_chat_fn(ctx.active_system_prompt or "", messages_for_main)
    print(main_response)

    # ── STEP 6: 落盘到 exports/turn_context/ ──────────────────────────────
    banner("6", "Export → demo/exports/turn_context/")
    dump(EXPORT_DIR / "00_workflow.md", f"""# Turn Context Workflow

```text
load fixtures/
  MEMORY.md + USER.md  → TeachingMemoryStore.load_from_disk()
                       → frozen blocks → system_prompt (cached)
  long_conversation.md → conversation_history (no system row)

build_turn_context(...)
  ├─ append user message
  ├─ active_system_prompt = cached (MEMORY+USER)
  ├─ preflight estimate ~{ctx.preflight_tokens_before} tokens
  ├─ should_compress? → {ctx.compression_ran}
  ├─ compress middle → SUMMARY_PREFIX message
  │     (+ on_pre_compress hint from MEMORY/USER)
  ├─ memory prefetch
  └─ return TurnContext(messages={len(ctx.messages)})
```

- turn_id: `{ctx.turn_id}`
- compressed: `{ctx.compression_ran}`
- tokens before/after: `{ctx.preflight_tokens_before}` → `{ctx.preflight_tokens_after}`
- model: `{DEEPSEEK_MODEL}`
- memory entries: `{len(store.memory_entries)}` / user entries: `{len(store.user_entries)}`
""")
    dump(
        EXPORT_DIR / "00_memory_block.md",
        store.format_for_system_prompt("memory") or "(empty)",
    )
    dump(
        EXPORT_DIR / "00_user_block.md",
        store.format_for_system_prompt("user") or "(empty)",
    )
    if ctx.compression_ran:
        dump(EXPORT_DIR / "01_aux_prompt.md", ctx.summarizer_prompt)
        dump(EXPORT_DIR / "02_aux_response.md", ctx.summarizer_response)
    dump(
        EXPORT_DIR / "03_main_system.md",
        ctx.active_system_prompt or "",
    )
    dump(
        EXPORT_DIR / "04_main_messages.md",
        format_messages_md(messages_for_main, title="Main LLM messages"),
    )
    dump(EXPORT_DIR / "05_main_response.md", main_response)

    banner("done", "Turn context demo finished")
    print(
        f"""
查看产物:
  {EXPORT_DIR.relative_to(HERE)}/

Fixtures:
  fixtures/MEMORY.md
  fixtures/USER.md
  fixtures/long_conversation.md

对照源码:
  ../hermes_src/tools/memory_tool.py           → MemoryStore.load_from_disk / format
  ../hermes_src/agent/turn_context.py          → build_turn_context
  ../hermes_src/agent/context_compressor.py    → compress / SUMMARY_PREFIX
  ../hermes_src/agent/conversation_compression.py → compress_context 编排
"""
    )
    return 0


if __name__ == "__main__":
    # Windows GBK console: prefer UTF-8 so Chinese logs/prompts print cleanly
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
