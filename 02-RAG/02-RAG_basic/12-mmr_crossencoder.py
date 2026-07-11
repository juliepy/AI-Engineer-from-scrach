# =============================================================================
#  MMR 去冗余选择  &  Cross-Encoder 精排
# =============================================================================
#
#  ── 完整流程图（对应本文件代码执行顺序）──────────────────────────────────────
#
#       ┌─────────────┐     ┌──────────────────────────────────────────┐
#       │   Query     │     │              CORPUS（语料库）              │
#       │ "员工年假天数"│     │  doc1, doc2, ... doc9（员工手册片段）     │
#       └──────┬──────┘     └──────────────────┬───────────────────────┘
#              │                                 │
#              └──────────────┬──────────────────┘
#                             ▼
#              ┌──────────────────────────────────────────┐
#              │  Bi-Encoder（bge-small-zh-v1.5）          │
#              │  bi_encoder_encode()                     │
#              │    encode(query)  ──► query_vec          │
#              │    encode(corpus) ──► doc_vecs           │
#              │    normalize_embeddings=True（L2 归一化）  │
#              └──────────────────┬───────────────────────┘
#                                 │
#                    sim_to_q = doc_vecs @ query_vec
#                                 │
#              ┌──────────────────┴───────────────────────┐
#              │                                          │
#              ▼                                          ▼
#  ┌───────────────────────────┐          ┌───────────────────────────────┐
#  │  Part 1: MMR 去冗余选择    │          │  Part 2: Bi-Encoder → CE 精排  │
#  └─────────────┬─────────────┘          └───────────────┬───────────────┘
#                │                                        │
#                ▼                                        ▼
#  ┌─────────────────────────┐              ┌─────────────────────────────┐
#  │ 路径 A：纯相关性 Top-K   │              │ bi_encoder_retrieve()       │
#  │ argsort(sim_to_q)[:K]  │              │ 按 cos 相似度取 Top-K 候选   │
#  │ → 易选入语义重复文档     │              └──────────────┬──────────────┘
#  └─────────────┬───────────┘                             │
#                │                                          ▼
#                ▼                             ┌─────────────────────────────┐
#  ┌─────────────────────────┐                  │ cross_encoder_rerank()      │
#  │ 路径 B：MMR 贪心选择     │                  │ CrossEncoder（bge-reranker） │
#  │ mmr_select(top_k=K)    │                  │ pairs = [[q,d1],[q,d2],...] │
#  │                         │                  │ predict() → CE 分数排序       │
#  │  初始化 selected=[],    │                  └──────────────┬──────────────┘
#  │        candidates=全部   │                                 │
#  │  ┌─ 循环 K 次 ────────┐  │                                 ▼
#  │  │ 对每个候选 i:       │  │                  ┌─────────────────────────────┐
#  │  │  rel  = sim_to_q[i]│  │                  │ Top-N 精排结果（N < K）      │
#  │  │  red  = max sim(i,  │  │                  │ 精度高于 Bi-Encoder 粗召回   │
#  │  │         selected)  │  │                  └─────────────────────────────┘
#  │  │  score=λ·rel       │  │
#  │  │       -(1-λ)·red   │  │
#  │  │  选最高分 → selected│  │
#  │  └────────────────────┘  │
#  └─────────────┬───────────┘
#                │
#                ▼
#  ┌─────────────────────────┐
#  │ MMR Top-K 多样化结果     │
#  │ 兼顾相关性 + 主题分散    │
#  └─────────────────────────┘
#
#  ── MMR 公式 ────────────────────────────────────────────────────────────────
#
#  score = λ · sim(doc, query) - (1-λ) · max_sim(doc, selected_docs)
#          ↑ 相关性权重 λ=0.5        ↑ 与已选文档的最大相似度（冗余惩罚）
#
#  ── 两阶段检索对比 ───────────────────────────────────────────────────────────
#
#  ┌────────────────────┬──────────────────────┬──────────────────────────────┐
#  │      阶段          │       模型           │           特点               │
#  ├────────────────────┼──────────────────────┼──────────────────────────────┤
#  │ Bi-Encoder 粗召回  │ bge-small-zh-v1.5    │ 快，query/doc 独立编码，ANN  │
#  │ MMR 去冗余         │ 同上（向量点积）      │ 在粗召回结果上提升多样性      │
#  │ Cross-Encoder 精排 │ bge-reranker-base    │ 慢，query-doc 联合编码，更准  │
#  └────────────────────┴──────────────────────┴──────────────────────────────┘
#
#  典型 RAG 串联：Query → Bi-Encoder Top-K →（可选 MMR）→ Cross-Encoder Top-N → LLM
#
# =============================================================================

import sys

import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

sys.stdout.reconfigure(encoding="utf-8")

# pip install sentence-transformers
bi_encoder = SentenceTransformer("BAAI/bge-small-zh-v1.5")
cross_encoder = CrossEncoder("BAAI/bge-reranker-base")

CORPUS = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "员工应遵守职业道德，保护公司机密。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
    "本公司年假为15天，入职满1年方可享受。",
    "年假按工龄累计，最长不超过15天。",
    "报销应提交发票原件及审批单。",
    "员工需遵守考勤制度，迟到需补卡。",
]

TOP_K = 4   # Bi-Encoder 粗召回 / MMR 选取数量
TOP_N = 2   # Cross-Encoder 精排后保留数量


# ── Part 1: MMR 贪心选择 ──────────────────────────────────────────────────────

def mmr_select(
    query_vec: np.ndarray,
    doc_vecs: np.ndarray,
    top_k: int,
    lambda_mult: float = 0.5,
) -> list[int]:
    """
    doc_vecs: shape (n, dim)，已归一化。
    向量归一化后余弦相似度 = 点积。
    """
    sim_to_q = doc_vecs @ query_vec
    selected: list[int] = []
    candidates = set(range(len(doc_vecs)))

    while len(selected) < top_k and candidates:
        best_idx, best_score = None, -1e9
        for i in candidates:
            redundancy = max(float(doc_vecs[i] @ doc_vecs[j]) for j in selected) if selected else 0.0
            score = lambda_mult * sim_to_q[i] - (1 - lambda_mult) * redundancy
            if score > best_score:
                best_score, best_idx = score, i
        selected.append(best_idx)   # type: ignore
        candidates.remove(best_idx) # type: ignore

    return selected


def bi_encoder_encode(
    query: str,
    corpus: list[str],
    model: SentenceTransformer,
) -> tuple[np.ndarray, np.ndarray]:
    """Bi-Encoder 编码：返回 (query_vec, doc_vecs)，均已 L2 归一化。"""
    doc_vecs = model.encode(corpus, normalize_embeddings=True)
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    return query_vec, doc_vecs


query = "员工年假天数"
query_vec, doc_vecs = bi_encoder_encode(query, CORPUS, bi_encoder)
sim_to_q = doc_vecs @ query_vec

naive_top_k = np.argsort(sim_to_q)[::-1][:TOP_K].tolist()
mmr_top_k = mmr_select(query_vec, doc_vecs, top_k=TOP_K, lambda_mult=0.5)

print(f"Query: {query}")
print(f"\n【对比：纯相关性 Top-{TOP_K}（易选入语义相近的重复内容）】")
for rank, idx in enumerate(naive_top_k, start=1):
    print(f"  Top-{rank} (cos={sim_to_q[idx]:.4f}): {CORPUS[idx]}")

print(f"\n【MMR Top-{TOP_K}（兼顾相关性与多样性）】")
for rank, idx in enumerate(mmr_top_k, start=1):
    print(f"  Top-{rank} (cos={sim_to_q[idx]:.4f}): {CORPUS[idx]}")


# ── Part 2: Bi-Encoder 召回 → Cross-Encoder 精排 ─────────────────────────────

def bi_encoder_retrieve(
    query: str,
    corpus: list[str],
    model: SentenceTransformer,
    top_k: int,
) -> list[tuple[str, float]]:
    """Bi-Encoder 向量检索：按余弦相似度取 Top-K。"""
    q_vec, doc_vecs = bi_encoder_encode(query, corpus, model)
    scores = doc_vecs @ q_vec
    ranked_idx = np.argsort(scores)[::-1][:top_k]
    return [(corpus[i], float(scores[i])) for i in ranked_idx]


def cross_encoder_rerank(
    query: str,
    candidates: list[str],
    reranker: CrossEncoder,
    top_n: int,
) -> list[tuple[str, float]]:
    """Cross-Encoder 精排：对 Top-K 候选重排取 Top-N。"""
    pairs = [[query, doc] for doc in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


bi_results = bi_encoder_retrieve(query, CORPUS, bi_encoder, top_k=TOP_K)

print(f"\n【Step 1】Bi-Encoder 粗召回 Top-{TOP_K}")
for rank, (doc, score) in enumerate(bi_results, start=1):
    print(f"  Top-{rank} (cos={score:.4f}): {doc}")

candidate_docs = [doc for doc, _ in bi_results]
reranked = cross_encoder_rerank(query, candidate_docs, cross_encoder, top_n=TOP_N)

print(f"\n【Step 2】Cross-Encoder 精排 Top-{TOP_N}")
for rank, (doc, score) in enumerate(reranked, start=1):
    print(f"  Top-{rank} (ce={score:.4f}): {doc}")
 

# ── Part 3·Bi-Encoder 召回 → mmr去冗余 → Cross-Encoder 精排 ─────────────────────────────

def bi_encoder_retrieve_mmr(
    query: str,
    corpus: list[str],
    model: SentenceTransformer,
    top_k: int,
) -> list[tuple[str, float]]:
    """Bi-Encoder 向量检索：按余弦相似度取 Top-K。"""
    q_vec, doc_vecs = bi_encoder_encode(query, corpus, model)
    scores = doc_vecs @ q_vec
    ranked_idx = np.argsort(scores)[::-1][:top_k]
    return [(corpus[i], float(scores[i])) for i in ranked_idx]

def mmr_select(
    query_vec: np.ndarray,
    doc_vecs: np.ndarray,
    top_k: int,
    lambda_mult: float = 0.5,
) -> list[int]:
    """MMR 贪心选择：按余弦相似度取 Top-K。"""
    sim_to_q = doc_vecs @ query_vec
    selected: list[int] = []
    candidates = set(range(len(doc_vecs)))
    while len(selected) < top_k and candidates:
        best_idx, best_score = None, -1e9
        for i in candidates:
            redundancy = max(float(doc_vecs[i] @ doc_vecs[j]) for j in selected) if selected else 0.0
            score = lambda_mult * sim_to_q[i] - (1 - lambda_mult) * redundancy
            if score > best_score:
                best_score, best_idx = score, i
        selected.append(best_idx) # type: ignore
        candidates.remove(best_idx) # type: ignore
    return selected

def cross_encoder_rerank_mmr(
    query: str,
    candidates: list[str],
    reranker: CrossEncoder,
    top_n: int,
) -> list[tuple[str, float]]:
    """Cross-Encoder 精排：对 Top-K 候选重排取 Top-N。"""
    pairs = [[query, doc] for doc in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

bi_results_mmr = bi_encoder_retrieve_mmr(query, CORPUS, bi_encoder, top_k=TOP_K)
mmr_selected = mmr_select(query_vec, doc_vecs, top_k=TOP_K, lambda_mult=0.5)
candidate_docs_mmr = [doc for doc, _ in bi_results_mmr]
reranked_mmr = cross_encoder_rerank_mmr(query, candidate_docs_mmr, cross_encoder, top_n=TOP_N)

print(f"\n【Step 1】Bi-Encoder 粗召回 Top-{TOP_K}")
for rank, (doc, score) in enumerate(bi_results_mmr, start=1):
    print(f"  Top-{rank} (cos={score:.4f}): {doc}")

print(f"\n【Step 2】MMR 去冗余 Top-{TOP_K}")
for rank, idx in enumerate(mmr_selected, start=1):
    print(f"  Top-{rank} (cos={sim_to_q[idx]:.4f}): {CORPUS[idx]}")

print(f"\n【Step 3】Cross-Encoder 精排 Top-{TOP_N}")
for rank, (doc, score) in enumerate(reranked_mmr, start=1):
    print(f"  Top-{rank} (ce={score:.4f}): {doc}")