"""
离线流水线 Step 4：向量索引（Vector Store）
使用 FAISS 构建 ANN（近似最近邻）索引，替代暴力余弦相似度
支持持久化 save/load，实现增量更新
"""
import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple
from .chunker import Chunk


class VectorStore:
    """
    基于 FAISS 的向量存储与检索
    index_path : 索引文件保存目录
    """

    def __init__(self, index_path: str = "./index"):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self._index = None        # FAISS index 对象
        self._chunks: List[Chunk] = []   # 与向量一一对应的文本块
        self._dim: int = 0

    # ──────────────────────── 写入 ────────────────────────

    def add(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """将文本块及其向量写入索引"""
        import faiss

        vectors = np.array(embeddings, dtype="float32")
        dim = vectors.shape[1]

        if self._index is None:
            self._dim = dim
            # IndexFlatIP：内积（等价于 L2 归一化后的余弦相似度）
            self._index = faiss.IndexFlatIP(dim)

        # L2 归一化，使内积 = 余弦相似度
        faiss.normalize_L2(vectors)
        self._index.add(vectors)
        self._chunks.extend(chunks)

        print(f"[VectorStore] 已写入 {len(chunks)} 个块，总计 {len(self._chunks)} 个块")

    # ──────────────────────── 检索 ────────────────────────

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[float, Chunk]]:
        """
        返回 top_k 个最相关块，格式：[(score, Chunk), ...]
        score 越大越相关（余弦相似度，范围 [-1, 1]）
        """
        import faiss

        if self._index is None or self._index.ntotal == 0:
            return []

        vec = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(vec)

        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append((float(score), self._chunks[idx]))
        return results

    # ──────────────────────── 持久化 ────────────────────────

    def save(self) -> None:
        """保存索引与文本块到磁盘"""
        import faiss
        if self._index is None:
            return

        faiss.write_index(self._index, str(self.index_path / "faiss.index"))
        with open(self.index_path / "chunks.pkl", "wb") as f:
            pickle.dump(self._chunks, f)
        with open(self.index_path / "meta.json", "w", encoding="utf-8") as f:
            json.dump({"dim": self._dim, "total": len(self._chunks)}, f)

        print(f"[VectorStore] 索引已保存至 {self.index_path}/")

    def load(self) -> bool:
        """从磁盘加载索引，返回是否成功"""
        import faiss
        index_file = self.index_path / "faiss.index"
        chunks_file = self.index_path / "chunks.pkl"

        if not index_file.exists() or not chunks_file.exists():
            return False

        self._index = faiss.read_index(str(index_file))
        with open(chunks_file, "rb") as f:
            self._chunks = pickle.load(f)
        with open(self.index_path / "meta.json", "r") as f:
            meta = json.load(f)
            self._dim = meta.get("dim", 0)

        print(f"[VectorStore] 加载成功，共 {len(self._chunks)} 个块")
        return True

    @property
    def total(self) -> int:
        return len(self._chunks)
