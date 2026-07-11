"""
离线流水线 Step 3：文本嵌入（Embedding）
使用本地 SentenceTransformer，无需 API Key，离线可用。
归一化后余弦相似度 = 点积，与 FAISS IndexFlatIP 配合使用。
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """
    文本向量化器（本地模型）
    model      : HuggingFace 模型名，默认中文 bge-small
    batch_size : 每批编码文本数
    """

    def __init__(
        self,
        api_key: str | None = None,          # 保留参数兼容 Pipeline 调用签名，不使用
        model: str = "BAAI/bge-small-zh-v1.5",
        batch_size: int = 32,
    ):
        self.batch_size = batch_size
        print(f"[Embedder] 加载本地模型：{model}")
        self._model = SentenceTransformer(model)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入，返回 L2 归一化向量列表。"""
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i: i + self.batch_size]
            vecs = self._model.encode(batch, normalize_embeddings=True).astype("float32")
            all_embeddings.extend(vecs.tolist())
        return all_embeddings

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]
