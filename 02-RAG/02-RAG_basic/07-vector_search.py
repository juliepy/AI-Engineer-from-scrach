# =============================================================================
#  6.1 向量检索（语义相似度）
# =============================================================================
#
#  原理：将 Query 与文档块分别 embedding，做 Top-K 最近邻（余弦/内积）。
#  优势：理解语义，"发薪日" 能匹配 "工资发放时间"。
#  短板：专有名词、型号、编号等精确匹配不如关键词检索。
#
#  ┌──────────────┐        ┌──────────────┐
#  │  文档块语料   │        │    Query     │
#  └──────┬───────┘        └──────┬───────┘
#         │ encode()              │ encode()
#         ▼                       ▼
#  ┌──────────────┐        ┌──────────────┐
#  │  文档 向量    │        │  查询 向量   │
#  └──────┬───────┘        └──────┬───────┘
#         │   faiss.IndexFlatIP   │
#         └───────────┬───────────┘
#                     │ index.search(q, k)
#                     ▼
#             Top-K 相似文档（余弦相似度）
#
# =============================================================================

import sys
import faiss
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding="utf-8")

texts = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "员工应遵守职业道德，保护公司机密。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
]

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
corpus_emb = model.encode(texts, normalize_embeddings=True).astype("float32")

# 归一化后内积 = 余弦相似度
index = faiss.IndexFlatIP(corpus_emb.shape[1])
index.add(corpus_emb)

query = "公司什么时候发工资？"
q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
scores, indices = index.search(q_emb, k=2)

print(f"Query: {query}")
for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
    print(f"  Top-{rank} (score={score:.4f}): {texts[idx]}")
