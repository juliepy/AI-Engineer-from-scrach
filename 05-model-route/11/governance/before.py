from dataclasses import dataclass
from typing import List


@dataclass
class RetrievalResult:
    doc_id: str
    text: str
    score: float


def retrieve(query: str, corpus: List[RetrievalResult], top_k: int = 3) -> List[RetrievalResult]:
    """事前：检索 grounding 材料。"""
    ranked = sorted(corpus, key=lambda r: r.score, reverse=True)
    return ranked[:top_k]


def build_grounded_prompt(query: str, docs: List[RetrievalResult]) -> str:
    ctx = "\n".join(f"[{d.doc_id}] {d.text}" for d in docs)
    return f"仅依据以下资料回答，无依据则拒答。\n{ctx}\n\n问题：{query}"
