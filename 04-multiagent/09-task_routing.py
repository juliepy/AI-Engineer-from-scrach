# =============================================================================
#  任务分配：能力匹配 + 负载均衡
# =============================================================================
#
#  分配策略在「匹配度」与「治理成本」间权衡：
#  - 能力路由：任务所需 skill ⊆ Agent skills
#  - 负载均衡：在合格 Agent 中选当前任务数最少者
#  - 动态：超载时可改派（此处用阈值示意）
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#    Task(skill, desc)
#       │
#       ▼
#    过滤 skills 匹配的 Agent
#       │
#       ▼
#    选 load 最小者 assign
#       │
#       ▼
#    load += 1；执行完成后 load -= 1
#
# =============================================================================

import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class Agent:
    name: str
    skills: List[str]
    load: int = 0
    max_load: int = 2


@dataclass
class Task:
    id: str
    skill: str
    description: str


def pick_agent(agents: List[Agent], skill: str) -> Optional[Agent]:
    """能力匹配 + 最小负载；超载 Agent 跳过。"""
    candidates = [
        a for a in agents if skill in a.skills and a.load < a.max_load
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda a: a.load)


def route_tasks(
    agents: List[Agent],
    tasks: List[Task],
    executor: Callable[[Agent, Task], str],
) -> Dict[str, str]:
    results: Dict[str, str] = {}
    pending: List[Task] = []

    for task in tasks:
        agent = pick_agent(agents, task.skill)
        if agent is None:
            pending.append(task)
            continue
        agent.load += 1
        results[task.id] = executor(agent, task)
        agent.load -= 1

    for task in pending:
        results[task.id] = f"[未分配] 无可用 {task.skill} Agent（负载已满或缺技能）"
    return results


def mock_execute(agent: Agent, task: Task) -> str:
    return f"{agent.name} 执行 {task.id}（load 峰值={agent.load}）: {task.description}"


if __name__ == "__main__":
    agents = [
        Agent("backend-a", ["python", "api"], load=0),
        Agent("backend-b", ["python", "api"], load=1, max_load=2),
        Agent("frontend-a", ["react", "ui"]),
        Agent("analyst-a", ["analysis"]),
    ]
    tasks = [
        Task("t1", "api", "实现 POST /login"),
        Task("t2", "api", "实现 GET /me"),
        Task("t3", "api", "补充集成测试"),
        Task("t4", "ui", "登录页表单"),
        Task("t5", "analysis", "输出需求摘要"),
        Task("t6", "go", "遗留服务补丁"),  # 无匹配技能
    ]

    print("=== 能力匹配 + 负载均衡路由 ===")
    for tid, msg in route_tasks(agents, tasks, mock_execute).items():
        print(f"  {tid}: {msg}")
    print()

    print("=== 各 Agent 技能与当前负载 ===")
    for a in agents:
        print(f"  {a.name}: skills={a.skills}, load={a.load}/{a.max_load}")
