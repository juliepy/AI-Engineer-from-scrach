# =============================================================================
#  向量数据库基础示例：FAISS + SentenceTransformer
# =============================================================================
#
#  ┌─────────────────────────────────────────────────────────────────────────┐
#  │                         文本语料 (texts)                                  │
#  └────────────────────────────┬────────────────────────────────────────────┘
#                               │  SentenceTransformer.encode()
#                               │  normalize_embeddings=True（向量归一化）
#                               ▼
#                      float32 向量矩阵 (N × dim)
#                               │
#                               │  faiss.IndexFlatIP.add()
#                               ▼
#                    ┌──────────────────────┐
#                    │   FAISS 内积索引      │  归一化后内积 = 余弦相似度
#                    │   IndexFlatIP(dim)   │
#                    └──────────┬───────────┘
#                               │
#              Query ──► encode ──► index.search(q, k)
#                               │
#                               ▼
#                    Top-K 相似文本 (scores + indices)
#
# =============================================================================

import sys
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding="utf-8")

# ── 语料 ──────────────────────────────────────────────────────────────────────
texts = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "员工应遵守职业道德，保护公司机密。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
]

# ── 1. 加载 Embedding 模型 ────────────────────────────────────────────────────
print("【1】加载模型并编码语料...")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
corpus_emb = model.encode(texts, normalize_embeddings=True).astype("float32")
dim = corpus_emb.shape[1]
print(f"  语料数量: {len(texts)}  向量维度: {dim}")

# ── 2. 构建 FAISS 索引 ────────────────────────────────────────────────────────
print("\n【2】构建 FAISS IndexFlatIP 索引（内积 = 余弦相似度）")
index = faiss.IndexFlatIP(dim)
index.add(corpus_emb)
print(f"  索引中向量数: {index.ntotal}")

# ── 3. 检索 ───────────────────────────────────────────────────────────────────
queries = [
    "公司什么时候发工资？",
    "每年可以休多少天假？",
]

print("\n【3】检索 Top-2 最相似文本")
print("-" * 60)
for query in queries:
    q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = index.search(q_emb, k=2)
    print(f"Query: {query}")
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        print(f"  Top-{rank} (score={score:.4f}): {texts[idx]}")
    print()
