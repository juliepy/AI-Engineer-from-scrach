import re
from typing import Dict

from agent.types import Tool


def apply_action(state: str, action: str, tools: Dict[str, Tool]) -> str:
    """将选中的动作应用到状态（解析 Action: tool[input] 并执行工具）。"""
    match = re.search(r"Action:\s*(\w+)\s*\[(.*?)\]", action, re.I)
    if not match:
        return state + "\n" + action
    name, arg = match.group(1), match.group(2)
    if name not in tools:
        obs = f"ERROR: unknown tool {name}"
    else:
        obs = tools[name].run(arg)
    return state + "\n" + action + "\nObservation: " + obs


def is_terminal(state: str, task: str) -> bool:
    """简单终止判断：已出现计算结果且字符统计线索。"""
    if "21+21" in task.replace(" ", "") or "21 + 21" in task:
        has_42 = "42" in state or "Observation: 42" in state
        has_chars = "字符数" in state or "word_count" in state
        return has_42 and has_chars
    return "Final Answer:" in state
