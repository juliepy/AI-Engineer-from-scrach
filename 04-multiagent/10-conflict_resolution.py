# =============================================================================
#  冲突解决：投票 vs 主席裁决（附证据权重示意）
# =============================================================================
#
#  多 Agent 输出不一致时需仲裁，防「假独立」与集体偏误：
#  - 投票：民主但可能被同质化 Agent 拉高一致错觉
#  - 主席：效率高但主席偏见风险
#  - 证据：提案附带可核查依据，加权计票
#
# =============================================================================

import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class Proposal:
    agent: str
    choice: str
    evidence_score: float  # 0~1，可核查程度


def resolve_by_vote(proposals: List[Proposal]) -> Tuple[str, Dict[str, int]]:
    """简单多数票；同票时 evidence_score 求和决胜。"""
    votes: Dict[str, int] = {}
    evidence_sum: Dict[str, float] = {}
    for p in proposals:
        votes[p.choice] = votes.get(p.choice, 0) + 1
        evidence_sum[p.choice] = evidence_sum.get(p.choice, 0.0) + p.evidence_score
    best = max(
        votes.keys(),
        key=lambda c: (votes[c], evidence_sum[c]),
    )
    return best, votes


def resolve_by_chair(
    proposals: List[Proposal],
    chair: Callable[[List[Proposal]], str],
) -> str:
    """主席听取全部提案后单方拍板。"""
    return chair(proposals)


def mock_chair(proposals: List[Proposal]) -> str:
    """主席采信单条最强证据（架构师背书），而非简单多数票。"""
    best = max(proposals, key=lambda p: p.evidence_score)
    return best.choice


if __name__ == "__main__":
    proposals = [
        Proposal("dev-a", "REST", 0.6),
        Proposal("dev-b", "REST", 0.5),
        Proposal("architect", "gRPC", 0.9),
        Proposal("qa", "REST", 0.4),
    ]

    print("=== 各 Agent 提案 ===")
    for p in proposals:
        print(f"  {p.agent}: {p.choice} (evidence={p.evidence_score})")
    print()

    winner, tally = resolve_by_vote(proposals)
    print(f"=== 投票结果：{winner} ===")
    print(f"  票型: {tally}")
    print()

    chair_pick = resolve_by_chair(proposals, mock_chair)
    print(f"=== 主席裁决：{chair_pick} ===")
    print("  （主席按 evidence 总分选 gRPC，与简单票选 REST 不同 → 展示仲裁差异）")
