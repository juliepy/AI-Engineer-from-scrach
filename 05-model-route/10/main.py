# =============================================================================
#  L1/L2 精确缓存 vs 语义缓存风险
# =============================================================================

import sys

from cache import ExactCache, RISK_NOTES, SemanticCache

sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    exact = ExactCache()
    exact.set("sys", "什么是 RAG？", "gpt-4o", "RAG 是检索增强生成。")
    print("=== 精确缓存 ===")
    print(f"  同 prompt 命中: {exact.get('sys', '什么是 RAG？', 'gpt-4o')}")
    print(f"  换措辞 miss:    {exact.get('sys', 'RAG 是什么？', 'gpt-4o')}")
    print()

    sem = SemanticCache(threshold=0.6)
    sem.set("如何取消我的订单？", "请登录后在订单页点击取消。")
    q = "我想取消订单怎么办"
    ans, score, matched = sem.get(q)
    print("=== 语义缓存（演示误命中风险）===")
    print(f"  新问法: {q}")
    print(f"  匹配到: {matched}  相似度={score:.2f}")
    print(f"  返回答案: {ans}")
    print()

    sem2 = SemanticCache(threshold=0.6)
    sem2.set("查询订单物流", "请在订单详情查看物流单号。")
    q2 = "取消订单"
    ans2, score2, matched2 = sem2.get(q2)
    print("=== 语义误命中示例 ===")
    print(f"  问: {q2}  最佳匹配: {matched2}  score={score2:.2f}  答案: {ans2}")
    print("  → 查询 vs 取消 被相似词「订单」拉近，可能答非所问")
    print()
    print("=== 语义缓存风险清单 ===")
    for i, note in enumerate(RISK_NOTES, 1):
        print(f"  {i}. {note}")
