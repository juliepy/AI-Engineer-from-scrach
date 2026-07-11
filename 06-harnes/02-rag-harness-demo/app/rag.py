from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.chunker import chunk_text
from app.generator import generate_answer
from app.indexer import TfidfIndex
from app.retriever import retrieve


@dataclass
class QueryResult:
    query: str
    answer: str
    hits: list[dict]


@dataclass
class RAGPipeline:
    index: TfidfIndex = field(default_factory=TfidfIndex)

    def ingest_text(self, doc_id: str, text: str) -> int:
        chunks = chunk_text(doc_id, text)
        self.index.add_chunks(chunks)
        return len(chunks)

    def ingest_directory(self, directory: Path, pattern: str = "*.txt") -> int:
        total = 0
        for path in sorted(directory.glob(pattern)):
            doc_id = path.stem
            total += self.ingest_text(doc_id, path.read_text(encoding="utf-8"))
        return total

    def query(self, question: str, top_k: int = 3) -> QueryResult:
        hits = retrieve(self.index, question, top_k=top_k)
        answer = generate_answer(question, hits)
        hit_payload = [
            {
                "doc_id": hit.chunk.doc_id,
                "chunk_index": hit.chunk.index,
                "text": hit.chunk.text,
                "score": round(hit.score, 4),
            }
            for hit in hits
        ]
        return QueryResult(query=question, answer=answer, hits=hit_payload)

    @property
    def chunk_count(self) -> int:
        return self.index.size
