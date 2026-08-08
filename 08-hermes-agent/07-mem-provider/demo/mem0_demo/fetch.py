"""05 · Fetch path: on_turn_start / prefetch_all → fence → mem0_search.

Mirrors agent/turn_context.py prologue + conversation_loop user injection.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict


def _raw_from_search(search_raw: str) -> str:
    try:
        search_obj = json.loads(search_raw)
        lines = []
        for item in (
            search_obj
            if isinstance(search_obj, list)
            else search_obj.get("results", [])
        ):
            if isinstance(item, dict) and item.get("memory"):
                lines.append(f"- {item['memory']}")
            elif isinstance(item, str):
                lines.append(f"- {item}")
        if lines:
            return "## Mem0 Memory\n" + "\n".join(lines)
    except Exception:
        pass
    return ""


def run_fetch_turn(
    mgr: Any,
    provider: Any,
    build_memory_context_block: Any,
    *,
    session_id: str,
) -> Dict[str, Any]:
    """Turn 2 — recall + inject into api user message."""
    # provider kept for call-site symmetry with store; all hooks go through mgr
    _ = provider
    user = "What did I say about reply length and my project name?"

    # Same prologue as turn_context.py: manager.on_turn_start BEFORE prefetch_all
    mgr.on_turn_start(1, user)
    time.sleep(0.2)
    raw = mgr.prefetch_all(user, session_id=session_id)

    # Tool backstop — same routing as run_agent → memory_manager.handle_tool_call
    search_raw = mgr.handle_tool_call(
        "mem0_search", {"query": user, "top_k": 5}
    )
    if not (raw and raw.strip()):
        raw = _raw_from_search(search_raw)

    # conversation_loop: copy user msg + append fenced block (API-only)
    fenced = build_memory_context_block(raw) if raw else ""
    api_user = user + ("\n\n" + fenced if fenced else "")
    sp_block = mgr.build_system_prompt()

    # End-of-turn warm-up (paired with sync in real Hermes; demo already synced in T1)
    mgr.queue_prefetch_all(user, session_id=session_id)
    time.sleep(0.5)

    return {
        "user": user,
        "prefetch_raw": raw,
        "mem0_search_result": search_raw,
        "fenced_user_injection": fenced,
        "api_user_message": api_user,
        "system_prompt_block": sp_block,
    }
