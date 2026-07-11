"""
在线问答 Step 1：检索器
向量相似度 Top-K 检索 + 可选 MMR 去冗余
"""
from typing import List, Tuple
from .chunker import Chunk
from .embedder import Embedder
from .vector_store import VectorStore


class Retriever:
    """
    检索器：将用户 query 转为向量，从 VectorStore 中取回最相关 chunks
    use_mmr    : 是否使用 MMR（最大边际相关）去冗余，平衡相关性与多样性
    mmr_lambda : MMR 中相关性权重，1.0 = 纯相关性，0.0 = 纯多样性
    """

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        top_k: int = 5,
        use_mmr: bool = False,
        mmr_lambda: float = 0.7,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k
        self.use_mmr = use_mmr
        self.mmr_lambda = mmr_lambda

    def retrieve(self, query: str) -> List[Tuple[float, Chunk]]:
        """返回 [(score, Chunk), ...] 按相关性降序"""
        query_vec = self.embedder.embed_one(query)

        # 如果启用 MMR，先取更多候选再筛选
        fetch_k = self.top_k * 3 if self.use_mmr else self.top_k
        candidates = self.vector_store.search(query_vec, top_k=fetch_k)

        if self.use_mmr and len(candidates) > self.top_k:
            candidates = self._mmr(query_vec, candidates)

        return candidates[:self.top_k]

    # ──────────────────────── MMR 去冗余 ────────────────────────

    def _mmr(
        self,
        query_vec: List[float],
        candidates: List[Tuple[float, Chunk]],
    ) -> List[Tuple[float, Chunk]]:
        """
        Maximum Marginal Relevance：
        每轮选择「与 query 最相关」且「与已选文档最不相似」的块
        score = λ·sim(q, d) - (1-λ)·max_sim(d, selected)
        """
        import numpy as np

        selected: List[Tuple[float, Chunk]] = []
        remaining = list(candidates)

        # 预先为候选块做嵌入（已经在 VectorStore 存了，这里简化：用 relevance score 代替相似度计算）
        while remaining and len(selected) < self.top_k:
            best_score = -1e9
            best_item = None

            for score, chunk in remaining:
                # 与已选块的最大相似度（简化：用文本重叠率估算）
                redundancy = self._max_overlap(chunk.text, [c.text for _, c in selected])
                mmr_score = self.mmr_lambda * score - (1 - self.mmr_lambda) * redundancy

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_item = (score, chunk)

            if best_item:
                selected.append(best_item)
                remaining.remove(best_item)

        return selected

    def _max_overlap(self, text: str, others: List[str]) -> float:
        """简化的词汇重叠率，用于估算块间相似度"""
        if not others:
            return 0.0
        words = set(text.split())
        overlaps = [len(words & set(o.split())) / (len(words) + 1) for o in others]
        return max(overlaps)
