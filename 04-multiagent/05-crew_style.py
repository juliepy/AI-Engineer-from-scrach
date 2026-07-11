# =============================================================================
#  7.4 Crew 风格极简对照：角色 + 任务列表
# =============================================================================
#
#  伪代码级教学，不绑定 CrewAI 等具体版本号。
#  设计思想：先定义 Role（谁、目标、背景），再挂 Task（做什么、交给谁）。
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#    crew = (roles: List[Role], tasks: List[Task])
#       │
#       ▼
#    按 tasks 顺序执行
#       │
#       ├─ 找到 task.agent 对应 Role
#       ├─ goal + backstory + description + 上文摘要 → 调用 model
#       └─ 输出追加到上下文，供后续 Task 阅读
#
# =============================================================================

import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class Role:
    name: str
    goal: str
    backstory: str


@dataclass
class Task:
    description: str
    agent: str


Crew = Tuple[List[Role], List[Task]]


def run_crew(
    crew: Crew,
    model: Callable[[str, str], str],
    user_goal: str = "",
) -> Dict[str, str]:
    """按任务列表顺序执行，每步由指定角色 agent 完成。"""
    roles, tasks = crew
    role_map = {r.name: r for r in roles}
    context = f"总目标: {user_goal}\n" if user_goal else ""
    outputs: Dict[str, str] = {}

    for task in tasks:
        role = role_map.get(task.agent)
        if role is None:
            raise KeyError(f"任务 '{task.description}' 找不到角色: {task.agent}")
        prompt = (
            f"你是 {role.name}。\n"
            f"目标: {role.goal}\n"
            f"背景: {role.backstory}\n\n"
            f"任务: {task.description}\n\n"
            f"[上下文]\n{context}"
        )
        out = model(role.name, prompt)
        outputs[task.description] = out
        context += f"\n[{role.name}] {task.description}:\n{out}\n"
    return outputs


def mock_model(agent_name: str, prompt: str) -> str:
    """占位 LLM，返回角色化短答。"""
    canned = {
        "PM": "用户故事：作为用户，我希望用账号密码登录并获得 token。",
        "Dev": "POST /login 接收 JSON，校验后返回 {'token': '...'}。",
        "QA": "用例：正确凭证返回 200；错误凭证返回 401。",
    }
    body = canned.get(agent_name, f"[{agent_name}] 占位输出")
    return f"{body}\n(prompt 长度={len(prompt)} 字符)"


if __name__ == "__main__":
    crew: Crew = (
        [
            Role("PM", "澄清需求", "擅长用户故事与验收标准。"),
            Role("Dev", "实现功能", "熟悉 REST API 与鉴权。"),
            Role("QA", "保障质量", "专注测试用例与风险点。"),
        ],
        [
            Task("写用户故事", "PM"),
            Task("实现 API", "Dev"),
            Task("编写测试用例", "QA"),
        ],
    )

    print("=== Crew 风格：角色 + 任务列表 ===")
    results = run_crew(crew, mock_model, user_goal="交付登录功能")
    for desc, text in results.items():
        print(f"--- {desc} ---")
        print(text)
        print()
