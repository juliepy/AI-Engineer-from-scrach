#!/usr/bin/env python3
"""Demonstrate MemoryManager prefetch fence + FakeProvider sync — no Hermes edits.

Imports real agent.memory_manager / memory_provider from hermes-agent on PYTHONPATH.
Does not call network backends.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEMO_ROOT = Path(__file__).resolve().parent
EXPORTS = DEMO_ROOT / "exports" / "mem_provider"
MODULE_ROOT = DEMO_ROOT.parent  # 07-mem-provider/


def _resolve_hermes_agent_root() -> Path:
    env = os.environ.get("HERMES_AGENT_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "agent" / "memory_manager.py").is_file():
            return p
        raise SystemExit(f"HERMES_AGENT_ROOT={p} missing agent/memory_manager.py")

    candidates = [
        MODULE_ROOT.parents[2] / "hermes-agent",
        MODULE_ROOT.parents[1] / "hermes-agent",
        Path.home() / "hermes-agent",
    ]
    for c in candidates:
        if (c / "agent" / "memory_manager.py").is_file():
            return c.resolve()
    raise SystemExit(
        "Cannot find hermes-agent. Set HERMES_AGENT_ROOT to the repo root."
    )


def main() -> int:
    root = _resolve_hermes_agent_root()
    sys.path.insert(0, str(root))

    from agent.memory_manager import MemoryManager, build_memory_context_block
    from agent.memory_provider import MemoryProvider

    class FakeProvider(MemoryProvider):
        def __init__(self) -> None:
            self.synced: List[Dict[str, Any]] = []
            self.queued: List[str] = []

        @property
        def name(self) -> str:
            return "fake"

        def is_available(self) -> bool:
            return True

        def initialize(self, session_id: str, **kwargs) -> None:
            return None

        def system_prompt_block(self) -> str:
            return "## Fake memory backend\nUse recalled facts from <memory-context>."

        def prefetch(self, query: str, *, session_id: str = "") -> str:
            return f"User previously said they like short answers. (query={query[:40]!r})"

        def queue_prefetch(self, query: str, *, session_id: str = "") -> None:
            self.queued.append(query)

        def sync_turn(
            self,
            user_content: str,
            assistant_content: str,
            *,
            session_id: str = "",
            messages: Optional[List[Dict[str, Any]]] = None,
        ) -> None:
            self.synced.append(
                {
                    "user": user_content,
                    "assistant": assistant_content,
                    "session_id": session_id,
                }
            )

        def get_tool_schemas(self) -> List[Dict[str, Any]]:
            return []

    mgr = MemoryManager()
    fake = FakeProvider()
    mgr.add_provider(fake)

    user = "What did I say about reply length?"
    # Turn start: fetch
    raw = mgr.prefetch_all(user)
    fenced = build_memory_context_block(raw)
    api_user = user + "\n\n" + fenced

    # System volatile piece
    sp_block = mgr.build_system_prompt()

    # Turn end: store + queue next prefetch
    asst = "You prefer concise replies."
    mgr.sync_all(user, asst, session_id="demo-sess")
    mgr.queue_prefetch_all(user, session_id="demo-sess")
    # Allow background worker to flush
    import time

    time.sleep(0.3)
    mgr.shutdown_all() if hasattr(mgr, "shutdown_all") else None

    EXPORTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hermes_agent_root": str(root),
        "source": "agent/memory_manager.py + FakeProvider",
        "prefetch_raw": raw,
        "fenced_user_injection": fenced,
        "api_user_message": api_user,
        "system_prompt_block": sp_block,
        "synced": fake.synced,
        "queued_prefetch": fake.queued,
        "prompts_to_read": [
            "agent/prompt_builder.py::MEMORY_GUIDANCE",
            "agent/background_review.py::_MEMORY_REVIEW_PROMPT",
            "build_memory_context_block system note",
        ],
    }
    (EXPORTS / "00_raw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    report = [
        "# Mem-provider demo",
        "",
        f"- hermes_agent_root: `{root}`",
        f"- generated: {payload['generated_at']}",
        "",
        "## 1. Prefetch → user injection (fetch)",
        "",
        "```",
        fenced,
        "```",
        "",
        "## 2. System prompt block (static)",
        "",
        "```",
        sp_block,
        "```",
        "",
        "## 3. After turn: sync_turn (store)",
        "",
        "```json",
        json.dumps(fake.synced, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Related prompts (read in notes/04)",
        "",
        "- `MEMORY_GUIDANCE`",
        "- `_MEMORY_REVIEW_PROMPT`",
        "- `<memory-context>` system note",
        "",
    ]
    (EXPORTS / "01_report.md").write_text("\n".join(report), encoding="utf-8")
    print(fenced[:200], "...")
    print(f"synced={fake.synced}")
    print(f"wrote {EXPORTS / '01_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
