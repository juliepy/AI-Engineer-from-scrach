# =============================================================================
#  6.4 RRF 多路排名融合（Reciprocal Rank Fusion）
# =============================================================================
#
#  原理：不依赖分数绝对值，只使用各路排名位置，公式：
#        RRF(d) = Σ  1 / (k + rank_i(d))
#  优势：无需归一化，对异常分数鲁棒，多路融合简单有效。
#  参数：k=60 是经验平滑常数，防止排名靠前的文档权重过大。
#
#                          Query
#                 ┌──────────┴──────────┐
#          向量检索路               BM25 检索路
#                 │                       │
#                 ▼                       ▼
#       [doc_2, doc_0, doc_4]   [doc_2, doc_3, doc_1]
#                 │                       │
#                 └──────────┬────────────┘
#                            │  RRF 融合
#                            │  score += 1 / (k + rank)
#                            ▼
#                    Top-K 融合结果（按 RRF 分降序）
#
# =============================================================================

import sys
from typing import Dict, List, Sequence

sys.stdout.reconfigure(encoding="utf-8")


def rrf_fuse(
    ranked_lists: Sequence[Sequence[str]],
    k: int = 60,
) -> List[tuple[str, float]]:
    """
    ranked_lists: 多路检索结果，每路为 doc_id 从优到劣的列表。
    k: 平滑常数，默认 60。
    """
    scores: Dict[str, float] = {}
    for ranks in ranked_lists:
        for rank, doc_id in enumerate(ranks, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ── 示例：向量路 Top-K 与 BM25 路 Top-K 的 doc_id 列表 ───────────────────────
texts = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",  # doc_0
    "标准工作时间为周一至周五，每天9:00-18:00。",          # doc_1
    "公司每月15日发放工资，提供五险一金、带薪年假。",      # doc_2
    "员工应遵守职业道德，保护公司机密。",                  # doc_3
    "年假：入职满1年可享受5天带薪年假，最多15天。",        # doc_4
]

# 模拟两路检索结果（doc_id 按相关性从高到低排列）
vec_ranked   = ["doc_2", "doc_4", "doc_0", "doc_1", "doc_3"]  # 向量检索排名
bm25_ranked  = ["doc_2", "doc_3", "doc_1", "doc_4", "doc_0"]  # BM25 检索排名

fused = rrf_fuse([vec_ranked, bm25_ranked], k=60)

print("RRF 融合结果：")
for rank, (doc_id, score) in enumerate(fused, start=1):
    idx = int(doc_id.split("_")[1])
    print(f"  Top-{rank} (rrf={score:.6f}) [{doc_id}]: {texts[idx]}")
