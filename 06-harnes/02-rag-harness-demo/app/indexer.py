from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from app.chunker import Chunk


@dataclass
class IndexedChunk:
    chunk: Chunk
    score: float


class TfidfIndex:
    """In-memory TF-IDF index for classroom demos (no vector DB required)."""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
        self._matrix = None

    @property
    def size(self) -> int:
        return len(self._chunks)

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        self._chunks.extend(chunks)
        texts = [c.text for c in self._chunks]
        self._matrix = self._vectorizer.fit_transform(texts)

    def search(self, query: str, top_k: int = 3) -> list[IndexedChunk]:
        if not query.strip() or self._matrix is None or not self._chunks:
            return []

        query_vec = self._vectorizer.transform([query])
        scores = linear_kernel(query_vec, self._matrix).flatten()
        ranked = sorted(
            ((idx, float(scores[idx])) for idx in range(len(self._chunks))),
            key=lambda item: item[1],
            reverse=True,
        )

        results: list[IndexedChunk] = []
        for idx, score in ranked[:top_k]:
            if score <= 0:
                continue
            results.append(IndexedChunk(chunk=self._chunks[idx], score=score))
        return results
