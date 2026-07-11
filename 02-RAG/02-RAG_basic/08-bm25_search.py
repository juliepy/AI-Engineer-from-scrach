# =============================================================================
#  6.2 关键词检索（BM25）
# =============================================================================
#
#  原理：BM25 是经典词频-逆文档频率加权排序函数，擅长精确词匹配。
#  优势：型号、编号、专有名词命中率高，计算轻量。
#  短板：无法理解语义，"发薪日" 无法匹配 "工资发放时间"。
#
#  ┌──────────────┐        ┌──────────────┐
#  │  文档块语料   │        │    Query     │
#  └──────┬───────┘        └──────┬───────┘
#         │ jieba.cut()           │ jieba.cut()
#         ▼                       ▼
#  ┌──────────────┐        ┌──────────────┐
#  │  分词 Token  │        │  分词 Token  │
#  └──────┬───────┘        └──────┬───────┘
#         │   BM25Okapi 构建索引  │
#         └───────────┬───────────┘
#                     │ bm25.get_scores(query_tokens)
#                     ▼
#             Top-K 相关文档（词频权重得分）
#
#  pip install rank_bm25 jieba
#
# =============================================================================

import sys
import jieba
from rank_bm25 import BM25Okapi

sys.stdout.reconfigure(encoding="utf-8")

texts = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假。",
    "员工应遵守职业道德，保护公司机密。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
]

# 中文分词后构建 BM25 索引
print("中文分词后构建 BM25 索引")
tokenized_corpus = [list(jieba.cut(doc)) for doc in texts]
bm25 = BM25Okapi(tokenized_corpus)

print("构建 BM25 索引完成")

print("开始查询")
query = "公司工资发放时间"
tokenized_query = list(jieba.cut(query))
scores = bm25.get_scores(tokenized_query)
print("查询完成")
print("分数：", scores)

# 按分数排序取 Top-2
top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:2]
print("排序完成")
print("Top-2 索引：", top_indices)

print(f"Query: {query}")
print("Top-2 结果：")
for rank, idx in enumerate(top_indices, start=1):
    print(f"  Top-{rank} (score={scores[idx]:.4f}): {texts[idx]}")
