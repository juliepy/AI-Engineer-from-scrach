from __future__ import annotations

from app.indexer import IndexedChunk, TfidfIndex


def retrieve(index: TfidfIndex, query: str, top_k: int = 3) -> list[IndexedChunk]:
    """Return top-k chunks ranked by lexical similarity."""
    return index.search(query, top_k=top_k)
