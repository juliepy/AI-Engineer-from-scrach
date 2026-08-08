"""06 · Write exports/mem_provider report artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .paths import EXPORTS


def write_exports(payload: Dict[str, Any]) -> Path:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    (EXPORTS / "00_raw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fenced = payload.get("fenced_user_injection") or ""
    search_raw = payload.get("mem0_search_result") or ""
    add_raw = payload.get("mem0_add_result")
    sp_block = payload.get("system_prompt_block") or ""
    turn1 = payload.get("turn1") or {}

    report = [
        "# Mem0 OSS demo (local)",
        "",
        f"- hermes_agent_root: `{payload.get('hermes_agent_root')}`",
        f"- HERMES_HOME (isolated): `{payload.get('hermes_home')}`",
        f"- backend: `{payload.get('backend')}`",
        f"- generated: {payload.get('generated_at')}",
        f"- sync_joined: `{turn1.get('sync_joined')}`",
        "",
        "## 1. Store — sync_turn (infer=True) + mem0_add",
        "",
        "Turn 1 goes through `MemoryManager.sync_all` → `Mem0MemoryProvider.sync_turn`",
        "→ OSS `backend.add(..., infer=True)` (LLM fact extraction).",
        "",
        "```json",
        add_raw if isinstance(add_raw, str) else json.dumps(add_raw, ensure_ascii=False),
        "```",
        "",
        "## 2. Fetch — prefetch → `<memory-context>` fence",
        "",
        "```",
        fenced or "(empty — check DeepSeek / embedder keys / search result below)",
        "```",
        "",
        "## 3. mem0_search tool (same OSS backend)",
        "",
        "```json",
        search_raw,
        "```",
        "",
        "## 4. System prompt block",
        "",
        "```",
        sp_block,
        "```",
        "",
    ]
    out = EXPORTS / "01_report.md"
    out.write_text("\n".join(report), encoding="utf-8")
    return out


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
