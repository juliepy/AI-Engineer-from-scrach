# =============================================================================
#  Token 估算 vs 账单对账
# =============================================================================
#
#  本地 tiktoken/字符估算 → 预算、限流、路由预检
#  API usage 回写         → 财务对账权威来源
#  二者 diff 超阈值       → 告警（编码差异、特殊 token、流式截断等）
#
# =============================================================================

import sys

from billing import UsageFromAPI, approx_token_count, reconcile, summarize

sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    samples = [
        ("req-1", "用三句话解释 RAG", UsageFromAPI(8, 42)),
        ("req-2", "写一段 500 字技术方案 " * 20, UsageFromAPI(620, 880)),
        ("req-3", "hello", UsageFromAPI(2, 15)),
    ]

    rows = []
    print("=== 估算 vs 账单 ===")
    for rid, text, usage in samples:
        est = approx_token_count(text)
        row = reconcile(rid, est, usage)
        rows.append(row)
        flag = " ⚠️ ALERT" if row.alert else ""
        print(
            f"  {rid}: 估算={row.estimated} 账单={row.billed} "
            f"diff={row.diff:+d} ({row.diff_pct}%){flag}"
        )
    print()
    print("汇总:", summarize(rows))
