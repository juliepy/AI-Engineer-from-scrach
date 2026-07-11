from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """A text segment tied to its source document."""

    doc_id: str
    text: str
    index: int


def chunk_text(doc_id: str, text: str, chunk_size: int = 200, overlap: int = 40) -> list[Chunk]:
    """Split text into overlapping fixed-size chunks for retrieval."""
    normalized = " ".join(text.split())
    if not normalized:
        return []

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(Chunk(doc_id=doc_id, text=piece, index=index))
            index += 1
        if end >= len(normalized):
            break
        start = end - overlap

    return chunks
