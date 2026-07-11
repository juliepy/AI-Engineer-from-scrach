# =============================================================================
#  8.4 企业职责链：数据脱敏后再分析
# =============================================================================
#
#  企业多 Agent 强调职责分离与合规：敏感操作（脱敏）在前，分析在后。
#  数据分析团队典型分工：数据工程师（SQL/脱敏）→ 分析师（洞察）→ 合规审计。
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#    raw_rows（含真实 user_id）
#       │
#       ▼
#    de_identify()  ── 合规 Agent / 数据工程师职责
#       │  哈希 / 泛化 / 抑制（此处用 "***" 示意）
#       ▼
#    safe_rows（分析师可见）
#       │
#       ▼
#    analyst_agent()  ── 分析师 Agent，仅接触脱敏数据
#       │
#       ▼
#    业务洞察（可审计、可对外展示）
#
# =============================================================================

import sys
from typing import Any, Dict, List

sys.stdout.reconfigure(encoding="utf-8")


def de_identify(table_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """合规步骤：脱敏后再交给下游 Agent。真实场景可用哈希/泛化/抑制。"""
    return [{"user": "***", "amount": r["amount"]} for r in table_rows]


def analyst_agent(rows: List[Dict[str, Any]]) -> str:
    """分析师 Agent：只应看到已脱敏数据。"""
    total = sum(r["amount"] for r in rows)
    return f"洞察：共 {len(rows)} 笔，总额 {total}"


def pipeline(raw_rows: List[Dict[str, Any]]) -> str:
    safe = de_identify(raw_rows)
    return analyst_agent(safe)


if __name__ == "__main__":
    raw_rows = [
        {"user": "u_10086", "amount": 1200},
        {"user": "u_10010", "amount": 800},
        {"user": "u_10000", "amount": 500},
    ]

    print("=== 原始数据（含敏感字段，分析师不可见）===")
    for row in raw_rows:
        print(f"  user={row['user']}, amount={row['amount']}")
    print()

    safe_rows = de_identify(raw_rows)
    print("=== 脱敏后（可交给分析师 Agent）===")
    for row in safe_rows:
        print(f"  user={row['user']}, amount={row['amount']}")
    print()

    print("=== 职责链 pipeline 输出 ===")
    print(pipeline(raw_rows))
