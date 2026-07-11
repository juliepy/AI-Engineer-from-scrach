# =============================================================================
#  单 Agent 长链 vs 多 Agent 分步（极简教学）
# =============================================================================
#
#  非真实框架，仅用极简类展示「上下文切分」的价值：
#
#  - 单 Agent：把所有子任务说明塞进一次调用 → Prompt 长、角色混杂、易漏步
#  - 多 Agent：每步短上下文，下一步只带必要摘要 → 专注、可控、可并行扩展
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#  【单 Agent 长链】
#    mega_prompt（需求分析 + 设计 + 编码 + 测试 + 审查）
#       │
#       ▼
#    model("single", mega_prompt) → 一次输出（易混、易超长）
#
#  【多 Agent 分步】
#    analyst → architect → coder（可继续扩展 tester / reviewer）
#       │         │          │
#       ▼         ▼          ▼
#    短 system_hint + 短 scratchpad → 每步独立调用
#       │
#       ▼
#    scratch = 上一步输出[:500]  摘要传递，控制上下文膨胀
#
# =============================================================================

import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class SimpleAgent:
    name: str
    system_hint: str
    # 真实场景此处应是 LLM 调用；这里用占位函数模拟
    model: Callable[[str, str], str]

    def run(self, user_input: str, scratchpad: str = "") -> str:
        prompt = (
            f"{self.system_hint}\n\n[上下文]\n{scratchpad}\n\n[用户]\n{user_input}"
        )
        return self.model(self.name, prompt)


def demo_single_long_chain(model: Callable[[str, str], str]) -> str:
    """单 Agent：把所有子任务说明塞进一次调用（易长、易混）。"""
    mega_prompt = (
        "你是全能助手。依次完成：需求分析、接口设计、写代码、写测试、审查。"
    )
    return model("single", mega_prompt)


def demo_multi_agents(model: Callable[[str, str], str]) -> Dict[str, str]:
    """多 Agent：每步短上下文，下一步只带必要摘要。"""
    roles: List[Tuple[str, str]] = [
        ("analyst", "你只输出需求要点列表。"),
        ("architect", "你只输出模块与接口草案。"),
        ("coder", "你只输出代码。"),
    ]
    outputs: Dict[str, str] = {}
    scratch = ""
    for name, hint in roles:
        agent = SimpleAgent(name, hint, model)
        out = agent.run("根据上一轮摘要继续。", scratchpad=scratch)
        outputs[name] = out
        scratch = out[:500]  # 教学用：摘要代替全文传递
    return outputs


def mock_model(agent_name: str, prompt: str) -> str:
    """占位 LLM：返回角色化短答，便于对比各步上下文长度。"""
    if agent_name == "single":
        return (
            f"[单 Agent 长链] 一次承担全部子任务，"
            f"prompt 长度={len(prompt)} 字符（角色多、指令堆叠）"
        )
    canned = {
        "analyst": "1. 用户需要登录模块\n2. 支持 JWT 鉴权\n3. 记录登录日志",
        "architect": "模块: auth\n接口: POST /login, GET /me\n依赖: token 中间件",
        "coder": "def login(username, password):\n    token = issue_jwt(username)\n    return {'token': token}",
    }
    body = canned.get(agent_name, f"[{agent_name}] 占位输出")
    return f"{body}\n\n(prompt 长度={len(prompt)} 字符)"


if __name__ == "__main__":
    print("=== 单 Agent 长链 ===")
    single_out = demo_single_long_chain(mock_model)
    print(single_out)
    print()

    print("=== 多 Agent 分步 ===")
    multi_out = demo_multi_agents(mock_model)
    for role, text in multi_out.items():
        print(f"--- {role} ---")
        print(text)
        print()
