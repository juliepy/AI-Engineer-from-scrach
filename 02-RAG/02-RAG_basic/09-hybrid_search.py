# =============================================================================
#  6.3 混合检索（Hybrid Search）
# =============================================================================
#
#  原理：BM25 分数 + 向量分数分别归一化后线性加权融合，兼顾语义与字面匹配。
#  公式：hybrid_score = alpha * vec_score + (1 - alpha) * bm25_score
#
#                          Query
#                 ┌──────────┴──────────┐
#          encode()                jieba.cut()
#                 │                       │
#                 ▼                       ▼
#       ┌─────────────────┐   ┌─────────────────┐
#       │   向量检索路     │   │   BM25 检索路   │
#       │  FAISS.search() │   │ bm25.get_scores()│
#       └────────┬────────┘   └────────┬────────┘
#                │ vec_scores           │ bm25_scores
#                │    min_max_norm()    │
#                └──────────┬───────────┘
#                           │
#               alpha * vec + (1-alpha) * bm25
#                           │
#                           ▼
#                   Top-K 融合结果
#
# =============================================================================

import sys
import numpy as np
import faiss
import jieba
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding="utf-8")

texts = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "员工应遵守职业道德，保护公司机密。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
]


def min_max_norm(scores: list[float]) -> list[float]:
    """
    归一化函数
    将分数列表归一化到 [0, 1] 之间
    scores: 分数列表
    return: 归一化后的分数列表
    """
    print("开始归一化")
    s_min, s_max = min(scores), max(scores)
    print("最小值：", s_min)
    print("最大值：", s_max)
    if s_max == s_min:
        return [1.0 for _ in scores] # 如果最大值和最小值相等，则返回全1
    return [(s - s_min) / (s_max - s_min) for s in scores] # 否则，归一化到 [0, 1] 之间


def hybrid_fuse(vec_scores: list[float], bm25_scores: list[float], alpha: float = 0.5) -> list[float]:
    print("开始融合")
    print("向量分数：", vec_scores)
    print("BM25分数：", bm25_scores)
    v = min_max_norm(vec_scores)
    print("向量分数归一化结果：", v)    
    print("向量分数归一化完成")
    b = min_max_norm(bm25_scores)
    print("BM25分数归一化结果：", b)
    print("BM25分数归一化完成")
    print("开始融合")
    print("融合结果：", [alpha * vi + (1 - alpha) * bi for vi, bi in zip(v, b)])
    print("融合完成")
    return [alpha * vi + (1 - alpha) * bi for vi, bi in zip(v, b)] # 返回融合后的分数列表


# ── 向量检索 ──────────────────────────────────────────────────────────────────

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
corpus_emb = model.encode(texts, normalize_embeddings=True).astype("float32")
index = faiss.IndexFlatIP(corpus_emb.shape[1])
index.add(corpus_emb)
print("向量检索完成")

# ── BM25 检索 ─────────────────────────────────────────────────────────────────
tokenized_corpus = [list(jieba.cut(doc)) for doc in texts]
bm25 = BM25Okapi(tokenized_corpus)
print("BM25检索完成")


# ── 融合 ──────────────────────────────────────────────────────────────────────
query = "公司工资发放时间"
print("开始查询")
q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
print("向量编码完成")

_, vec_indices = index.search(q_emb, k=len(texts))
vec_scores_raw = index.search(q_emb, k=len(texts))[0][0].tolist()
print("向量分数：", vec_scores_raw)
print("向量分数完成")

# BM25 保持与 texts 相同顺序
bm25_scores_raw = bm25.get_scores(list(jieba.cut(query))).tolist()
print("BM25分数：", bm25_scores_raw)
print("BM25分数完成")


# 向量分数也需要按 texts 顺序排列
vec_scores_ordered = [0.0] * len(texts)
for score, idx in zip(*index.search(q_emb, k=len(texts))):
    for s, i in zip(score, idx):
        vec_scores_ordered[i] = float(s)
print("向量分数排序完成")
print("向量分数：", vec_scores_ordered)
print("向量分数完成")

print("开始融合")
hybrid_scores = hybrid_fuse(vec_scores_ordered, bm25_scores_raw, alpha=0.5)
top_indices = sorted(range(len(hybrid_scores)), key=lambda i: hybrid_scores[i], reverse=True)[:2]
print("融合完成")
print("融合结果：", hybrid_scores)
print("融合完成")

print("开始排序")
print("排序结果：", sorted(range(len(hybrid_scores)), key=lambda i: hybrid_scores[i], reverse=True)[:2])
print("排序完成")

print(f"Query: {query}")
for rank, idx in enumerate(top_indices, start=1):
    print(f"  Top-{rank} (hybrid={hybrid_scores[idx]:.4f}): {texts[idx]}")
