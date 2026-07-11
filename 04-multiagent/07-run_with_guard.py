# =============================================================================
#  9.x 生产刹车：步数上限 + 重复计划检测
# =============================================================================
#
#  多 Agent 生产难点常在成本、延迟、稳定性、可观测。本示例演示简单「刹车」：
#  - max_steps：防止无限循环耗尽 Token / 预算
#  - seen 集合：检测重复 action，及时 abort
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#    for step in range(max_steps):
#       action = agent_step(transcript + goal)
#       action in seen? ──是──► RuntimeError（重复计划）
#       seen.add(action); transcript.append(action)
#       "DONE" in action? ──是──► return transcript
#    raise RuntimeError（步数超限）
#
#  ── 附：高频面试简答（Q16～Q18）──────────────────────────────────────────────
#
#  Q16：多 Agent 会不会降低一致性（前后端接口对不上）？
#  A：会。需单一契约源（OpenAPI/JSON Schema）+ 契约测试 Agent 或静态检查 + 状态机门禁。
#
#  Q17：如何做跨 Agent 的权限隔离？
#  A：工具分账户/分密钥；Agent 最小权限；敏感操作走审批工作流；审计日志不可篡改存储。
#
#  Q18：多 Agent 的评估怎么做？
#  A：分层——单元（单 Agent I/O）、集成（两两交互）、端到端（任务成功率）；
#     LLM-as-judge 需防偏，最好配黄金集与人审。
#
# =============================================================================

import sys
from typing import Callable, List, Set

sys.stdout.reconfigure(encoding="utf-8")


def run_with_guard(
    agent_step: Callable[[List[str]], str],
    user_goal: str,
    max_steps: int = 20,
) -> List[str]:
    transcript: List[str] = []
    seen: Set[str] = set()
    for _ in range(max_steps):
        action = agent_step(transcript + [f"GOAL: {user_goal}"])
        h = action.strip()
        if h in seen:
            raise RuntimeError("detected repeated action; abort")
        seen.add(h)
        transcript.append(action)
        if "DONE" in action:
            return transcript
    raise RuntimeError("max steps exceeded")


def demo_agent_ok(ctx: List[str]) -> str:
    """正常 Agent：三步后输出 DONE。"""
    step = len([x for x in ctx if not x.startswith("GOAL:")])
    plan = [
        "PLAN: 分析需求",
        "PLAN: 实现 API",
        "PLAN: 编写测试 DONE",
    ]
    return plan[min(step, len(plan) - 1)]


def demo_agent_repeat(ctx: List[str]) -> str:
    """失控 Agent：反复输出同一计划。"""
    return "PLAN: 继续分析需求"


def demo_agent_never_done(ctx: List[str]) -> str:
    """失控 Agent：每步不同但永不 DONE。"""
    step = len([x for x in ctx if not x.startswith("GOAL:")])
    return f"PLAN: 子任务 #{step + 1}"


if __name__ == "__main__":
    goal = "交付登录 API"

    print("=== 正常完成（含 DONE）===")
    ok = run_with_guard(demo_agent_ok, goal, max_steps=10)
    for i, line in enumerate(ok, 1):
        print(f"  {i}. {line}")
    print()

    print("=== 重复计划检测（应 abort）===")
    try:
        run_with_guard(demo_agent_repeat, goal, max_steps=10)
    except RuntimeError as e:
        print(f"  捕获: {e}")
    print()

    print("=== 步数上限（应超限）===")
    try:
        run_with_guard(demo_agent_never_done, goal, max_steps=5)
    except RuntimeError as e:
        print(f"  捕获: {e}")
