#!/usr/bin/env python3
"""Mem0 OSS demo entry — orchestrates setup → store → fetch → report.

LLM: DeepSeek API.
Embed default: HuggingFace Qwen/Qwen3-Embedding-0.6B (or ollama / openai).
See README / oss_setup.py.

Teaching modules live in mem0_demo/:
  paths → bootstrap → oss_setup → store → fetch → report
"""

from __future__ import annotations

from typing import Any, Dict

from mem0_demo.bootstrap import import_mem0_stack, resolve_hermes_agent_root
from mem0_demo.fetch import run_fetch_turn
from mem0_demo.oss_setup import prepare_hermes_home
from mem0_demo.paths import SESSION_ID, USER_ID
from mem0_demo.report import now_iso, write_exports
from mem0_demo.store import run_store_turn


def main() -> int:
    root = resolve_hermes_agent_root()
    hermes_home, mem0_cfg, backend_label = prepare_hermes_home()

    MemoryManager, Mem0MemoryProvider, build_memory_context_block = import_mem0_stack(
        root
    )

    mgr = MemoryManager()
    provider = Mem0MemoryProvider()
    mgr.add_provider(provider)
    mgr.initialize_all(SESSION_ID, user_id=USER_ID, platform="cli")

    if not provider.is_available():
        raise SystemExit(
            f"Mem0MemoryProvider reports unavailable. Check {hermes_home / 'mem0.json'}"
        )
    if getattr(provider, "_backend", None) is None:
        err = getattr(provider, "_init_error", "unknown")
        raise SystemExit(f"Mem0 OSS backend failed to init: {err}")

    # ★ 讲解点 1：存
    turn1 = run_store_turn(mgr, provider, session_id=SESSION_ID)
    # ★ 讲解点 2：取 + 围栏
    turn2 = run_fetch_turn(
        mgr, provider, build_memory_context_block, session_id=SESSION_ID
    )

    mgr.shutdown_all()

    payload: Dict[str, Any] = {
        "generated_at": now_iso(),
        "hermes_agent_root": str(root),
        "hermes_home": str(hermes_home),
        "backend": backend_label,
        "source": "plugins/memory/mem0 + agent/memory_manager.py (OSS / DeepSeek)",
        "mem0_json": mem0_cfg,  # no api_key fields; secrets stay in env
        "turn1": {
            "user": turn1["user"],
            "assistant": turn1["assistant"],
            "sync_joined": turn1["sync_joined"],
        },
        "mem0_add_result": turn1["mem0_add_result"],
        "prefetch_raw": turn2["prefetch_raw"],
        "mem0_search_result": turn2["mem0_search_result"],
        "fenced_user_injection": turn2["fenced_user_injection"],
        "api_user_message": turn2["api_user_message"],
        "system_prompt_block": turn2["system_prompt_block"],
    }
    report_path = write_exports(payload)

    fenced = turn2["fenced_user_injection"]
    raw = turn2["prefetch_raw"]
    search_raw = turn2["mem0_search_result"]
    print(f"backend={backend_label}")
    print((fenced or raw or search_raw)[:300], "...")
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
