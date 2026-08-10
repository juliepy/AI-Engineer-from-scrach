"""Backend package — keep imports lazy so `import backend.llm` does not pull torch/graph."""

from __future__ import annotations

from typing import Any

__all__ = ["chatbot", "ingest_rag_document", "get_all_threads"]


def __getattr__(name: str) -> Any:
    if name == "chatbot":
        from backend.startup_log import startup_log

        startup_log("[backend] importing graph ...")
        from backend.graph import chatbot

        return chatbot
    if name == "ingest_rag_document":
        from backend.startup_log import startup_log

        startup_log("[backend] importing rag ...")
        from backend.rag import ingest_rag_document

        return ingest_rag_document
    if name == "get_all_threads":
        from backend.startup_log import startup_log

        startup_log("[backend] importing threads ...")
        from backend.threads import get_all_threads

        return get_all_threads
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
