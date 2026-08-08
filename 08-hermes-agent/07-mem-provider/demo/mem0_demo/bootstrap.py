"""02 · Bootstrap: find hermes-agent, check deps, import Mem0 without package side effects."""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from typing import List, Tuple

from .paths import MODULE_ROOT


def resolve_hermes_agent_root() -> Path:
    env = os.environ.get("HERMES_AGENT_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "agent" / "memory_manager.py").is_file():
            return p
        raise SystemExit(f"HERMES_AGENT_ROOT={p} missing agent/memory_manager.py")

    candidates = [
        # 人工智能面试题/hermes-agent (sibling of AI_coding_interview)
        MODULE_ROOT.parents[2] / "hermes-agent",
        MODULE_ROOT.parents[1] / "hermes-agent",
        # Local teaching snapshot under 07-mem-provider/hermes_src
        MODULE_ROOT / "hermes_src",
        Path.home() / "hermes-agent",
        Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "hermes-agent",
    ]
    for c in candidates:
        if c and (c / "agent" / "memory_manager.py").is_file():
            return c.resolve()
    raise SystemExit(
        "Cannot find hermes-agent. Set HERMES_AGENT_ROOT to the repo root."
    )


def ensure_deps() -> None:
    missing: List[str] = []
    try:
        import mem0  # noqa: F401
    except ImportError:
        missing.append("mem0ai>=2.0.10,<3")
    try:
        import qdrant_client  # noqa: F401
    except ImportError:
        missing.append("qdrant-client")
    if missing:
        raise SystemExit(
            "Missing packages: "
            + ", ".join(missing)
            + "\nInstall:\n  pip install -r requirements.txt"
        )


def install_hermes_on_path(root: Path) -> None:
    sys.path.insert(0, str(root))


def stub_memory_plugin_packages(root: Path) -> None:
    """Avoid executing plugins.memory.__init__ (pulls yaml / hermes_cli.config)."""
    for name, path in (
        ("plugins", root / "plugins"),
        ("plugins.memory", root / "plugins" / "memory"),
    ):
        if name not in sys.modules:
            mod = types.ModuleType(name)
            mod.__path__ = [str(path)]  # type: ignore[attr-defined]
            mod.__package__ = name
            sys.modules[name] = mod


def import_mem0_stack(root: Path) -> Tuple[type, type, object]:
    """Import Hermes Mem0 wiring without loading full plugin package side effects.

    Returns three callables/types used by the demo:

    - MemoryManager
        Orchestrator over one or more memory providers. Demo calls its APIs
        (initialize_all / sync_all / prefetch_all / on_turn_start /
        handle_tool_call / queue_prefetch_all) the same way AIAgent does —
        never talk to Mem0 directly except via this manager.

    - Mem0MemoryProvider
        Concrete MemoryProvider plugin (OSSBackend → mem0.Memory.from_config).
        Registered with ``mgr.add_provider(...)``; owns sync_turn / prefetch /
        mem0_add / mem0_search against Qdrant + configured LLM/embedder.

    - build_memory_context_block
        Pure helper: turns prefetch text into a ``<memory-context>...</memory-context>``
        fence string. Runtime injects that into the *user* message (not system
        prompt) so prompt-cache stays stable.
    """
    install_hermes_on_path(root)
    ensure_deps()
    stub_memory_plugin_packages(root)

    from agent.memory_manager import MemoryManager, build_memory_context_block
    from plugins.memory.mem0 import Mem0MemoryProvider

    return MemoryManager, Mem0MemoryProvider, build_memory_context_block
