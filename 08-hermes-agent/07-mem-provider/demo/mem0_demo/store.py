"""04 · Store path: sync_all → sync_turn (infer=True) + mem0_add (verbatim).

Mirrors AIAgent._sync_external_memory_for_turn:
  sync_all(...) then queue_prefetch_all(...)
"""

from __future__ import annotations

import time
from typing import Any, Dict


def wait_provider_sync(provider: Any, timeout: float = 90.0) -> bool:
    """Mem0 sync_turn is itself async; join its worker after MemoryManager dispatches."""
    deadline = time.monotonic() + timeout
    time.sleep(0.4)
    while time.monotonic() < deadline:
        t = getattr(provider, "_sync_thread", None)
        if t is None:
            time.sleep(0.2)
            t2 = getattr(provider, "_sync_thread", None)
            if t2 is None:
                return True
            t = t2
        if not t.is_alive():
            return True
        t.join(timeout=1.0)
    return False


def run_store_turn(mgr: Any, provider: Any, *, session_id: str) -> Dict[str, Any]:
    """Turn 1 — write memories (LLM extract + verbatim seed)."""
    user = (
        "Please remember: I prefer short answers in Chinese, "
        "and my project codename is Orion."
    )
    assistant = "明白了。之后用中文短答，并记住项目代号 Orion。"

    # Real Hermes end-of-turn: MemoryManager.sync_all → provider.sync_turn
    mgr.sync_all(user, assistant, session_id=session_id)
    synced_ok = wait_provider_sync(provider, timeout=120.0)

    # Same helper also warms next-turn recall (Mem0.queue_prefetch is currently
    # a no-op; calling the manager keeps the demo on the Hermes contract).
    mgr.queue_prefetch_all(user, session_id=session_id)

    # Verbatim seed (infer=False) — routed like a model tool call via manager
    add_raw = mgr.handle_tool_call(
        "mem0_add",
        {
            "content": (
                "User prefers short answers in Chinese. "
                "Project codename is Orion."
            )
        },
    )
    return {
        "user": user,
        "assistant": assistant,
        "sync_joined": synced_ok,
        "mem0_add_result": add_raw,
    }

