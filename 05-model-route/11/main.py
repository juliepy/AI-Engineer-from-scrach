# =============================================================================
#  幻觉治理：事前 — 事中 — 事后
# =============================================================================
#
#  事前：RAG 检索 + 约束 Prompt（仅依据资料）
#  事中：Citation 校验、置信度阈值、拒答
#  事后：用户反馈、幻觉率统计、人工复盘
#
# =============================================================================

import sys

from governance import (
    AfterAudit,
    FeedbackRecord,
    RetrievalResult,
    build_grounded_prompt,
    check_during,
    refuse,
    retrieve,
)

sys.stdout.reconfigure(encoding="utf-8")

CORPUS = [
    RetrievalResult("d1", "公司年假为 10 个工作日。", 0.92),
    RetrievalResult("d2", "远程办公需每周到岗 2 天。", 0.75),
    RetrievalResult("d3", "报销截止日为次月 5 日。", 0.60),
]


def mock_llm(prompt: str) -> str:
    if "无相关内容" in prompt or len(prompt) < 30:
        return "公司年假 20 天。"  # 故意无 citation 的幻觉答案
    return "根据 [d1]，公司年假为 10 个工作日。"


if __name__ == "__main__":
    query = "公司年假有多少天？"
    docs = retrieve(query, CORPUS)
    prompt = build_grounded_prompt(query, docs)

    print("=== 事前：检索 + Grounded Prompt ===")
    print(f"  命中 {len(docs)} 条，首条 score={docs[0].score}")
    print()

    raw = mock_llm(prompt)
    print("=== 事中：Citation + 置信度校验 ===")
    check = check_during(raw, sources=["d1", "d2"], confidence=0.85)
    if check.allowed:
        print(f"  放行: {check.answer}")
    else:
        print(f"  拒答 ({check.reason}): {refuse(check.reason)}")

    bad = mock_llm("无相关内容")
    check_bad = check_during(bad, sources=["d1"], confidence=0.85)
    print(f"  幻觉样例拒答: {refuse(check_bad.reason)}")
    print()

    print("=== 事后：反馈与复盘 ===")
    audit = AfterAudit()
    audit.log_feedback(FeedbackRecord(query, raw, user_rating=5, flagged_hallucination=False))
    audit.log_feedback(
        FeedbackRecord("年假 30 天？", bad, user_rating=1, flagged_hallucination=True)
    )
    print(f"  幻觉率: {audit.hallucination_rate()}%")
    print(f"  需人工复盘: {audit.needs_review(threshold_pct=30)}")
