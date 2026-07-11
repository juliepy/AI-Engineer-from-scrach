# =============================================================================
#  Step-back 检索  &  重排序（Reranking）
# =============================================================================
#
#  ── Step-back（两次检索拼上下文）────────────────────────────────────────────
#
#  原理：对用户原始问题生成一个更抽象的"退一步"问题，两路检索后合并上下文，
#        让 LLM 同时拥有具体细节与背景知识。
#
#       用户问题 ──────────────────────────────► 具体检索结果 (concrete_ctx)
#            │                                          │
#            │ LLM 生成抽象问题                         │ merge()
#            ▼                                          │
#       抽象问题 ──────────────────────────────► 背景检索结果 (background_ctx)
#                                                       │
#                                                       ▼
#                                               final_prompt → LLM
#
#  ── 重排序（Reranking）───────────────────────────────────────────────────────
#
#  原理：向量检索（Bi-Encoder）为速度对 query-doc 独立编码，交互信息不足；
#        Cross-Encoder 把 query 与 doc 拼在一起打分，精度更高但慢，
#        故放在 Top-K 之后做小范围重排。
#
#       ┌──────────────────────────────────────────────────┐
#       │                  Bi-Encoder                      │
#       │  encode(query) ──► q_vec                         │  快，可 ANN
#       │  encode(doc)   ──► d_vec   score = q_vec · d_vec │  精度低于 CE
#       └──────────────────────────────────────────────────┘
#
#       ┌──────────────────────────────────────────────────┐
#       │                 Cross-Encoder                    │
#       │  encode([query, doc]) ──► score                  │  精度高
#       │  query 与 doc 深度交互（Self-Attention）          │  慢，小批量
#       └──────────────────────────────────────────────────┘
#
#  流程：
#       Query ──► Bi-Encoder 向量检索 ──► Top-K 候选
#                                              │
#                                   Cross-Encoder 重排序
#                                              │
#                                         Top-N 结果（N < K）
#
# =============================================================================

from datetime import datetime
import sys

sys.stdout.reconfigure(encoding="utf-8")


# ── Part 1: Step-back 查询生成 ────────────────────────────────────────────────

def step_back_queries(user_question: str) -> tuple[str, str]:
    """
    第二步可用 LLM 生成 abstract_q；此处用占位演示结构。
    返回 (具体问题, 抽象退步问题)
    """
    abstract_q = f"与下列问题相关的背景原理与定义是什么？{user_question}"
    return user_question, abstract_q


question = "公司每月几号发工资？"
q1, q2 = step_back_queries(question)

print("【Step-back 查询】")
print(f"  具体问题：{q1}")
print(f"  抽象问题：{q2}")

# concrete_ctx   = retriever.invoke(q1)
# background_ctx = retriever.invoke(q2)
# final_prompt   = merge(concrete_ctx, background_ctx)


# ── Part 2: Bi-Encoder 召回 → Cross-Encoder 重排 ─────────────────────────────

# pip install sentence-transformers
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

TOP_K = 4   # Bi-Encoder 粗召回数量
TOP_N = 2   # Cross-Encoder 精排后保留数量

print(" load bi-encoder and cross-encoder start time:")
time_start = datetime.now()
bi_encoder = SentenceTransformer("BAAI/bge-small-zh-v1.5")
cross_encoder = CrossEncoder("BAAI/bge-reranker-base")
print(" load bi-encoder and cross-encoder end time:")
time_end = datetime.now()
print(f" load bi-encoder and cross-encoder time: {time_end - time_start}")


def bi_encoder_retrieve(
    query: str,
    corpus: list[str],
    model: SentenceTransformer,
    top_k: int,
) -> list[tuple[str, float]]:
    """Bi-Encoder 向量检索：query 与 doc 独立编码，按余弦相似度取 Top-K。"""
    doc_vecs = model.encode(corpus, normalize_embeddings=True)
    q_vec = model.encode([query], normalize_embeddings=True)[0]
    scores = doc_vecs @ q_vec
    ranked_idx = np.argsort(scores)[::-1][:top_k]
    return [(corpus[i], float(scores[i])) for i in ranked_idx]


def cross_encoder_rerank(
    query: str,
    candidates: list[str], 
    reranker: CrossEncoder,
    top_n: int,
) -> list[tuple[str, float]]:
    """Cross-Encoder 精排：query 与 doc 联合编码，对 Top-K 候选重排取 Top-N。"""
    pairs = [[query, doc] for doc in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


corpus = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
    "员工应遵守职业道德，保护公司机密。",
    "报销应提交发票原件及审批单。",
    "年假按工龄累计，最长不超过15天。",
    "员工需遵守考勤制度，迟到需补卡。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
    "员工应遵守职业道德，保护公司机密。",
    "报销应提交发票原件及审批单。",
    "年假按工龄累计，最长不超过15天。",
    "员工需遵守考勤制度，迟到需补卡。",
]

query = "发工资"

# Step 1: Bi-Encoder 粗召回
print(" bi-encoder start time:")
time_start = datetime.now()
bi_results = bi_encoder_retrieve(query, corpus, bi_encoder, top_k=TOP_K)

print(" bi-encoder end time:")
time_end = datetime.now()
print(f" bi-encoder time: {time_end - time_start}")
print(f"\n【Step 1】Bi-Encoder 粗召回 Top-{TOP_K}")
for rank, (doc, score) in enumerate(bi_results, start=1):
    print(f"  Top-{rank} (cos={score:.4f}): {doc}")

# Step 2: Cross-Encoder 精排
print(" cross-encoder start time:")
time_start = datetime.now()
candidate_docs = [doc for doc, _ in bi_results]
reranked = cross_encoder_rerank(query, candidate_docs, cross_encoder, top_n=TOP_N)
print(" cross-encoder end time:")
time_end = datetime.now()
print(f" cross-encoder time: {time_end - time_start}")
print(f"\n【Step 2】Cross-Encoder 精排 Top-{TOP_N}")
for rank, (doc, score) in enumerate(reranked, start=1):
    print(f"  Top-{rank} (ce={score:.4f}): {doc}")
