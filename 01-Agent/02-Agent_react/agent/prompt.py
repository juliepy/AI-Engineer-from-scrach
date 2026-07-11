from typing import Dict, List, Tuple

from agent.types import Tool

# history 每条为 (thought, action, action_input, observation)
HistoryItem = Tuple[str, str, str, str]


def build_prompt(
    question: str,
    history: List[HistoryItem],
    tools: Dict[str, Tool],
) -> str:
    tool_names = "[" + ", ".join(tools.keys()) + "]"
    tool_desc = "\n".join(f"- {t.name}: {t.description}" for t in tools.values())
    lines = [
        "You solve tasks with tools. Use EXACTLY this format each turn:",
        "Thought: ...",
        f"Action: one of {tool_names}",
        "Action Input: ...",
        "Stop when you can answer:",
        "Final Answer: ...",
        "",
        "IMPORTANT: Output only ONE turn per response. Do not include Final Answer until you have received Observation from a tool.",
        f"Tools available: {tool_names}",
        "Tool descriptions:",
        tool_desc,
        "",
        f"Question: {question}",
        "",
    ]
    for thought, action, action_input, obs in history:
        lines += [
            f"Thought: {thought}",
            f"Action: {action}",
            f"Action Input: {action_input}",
            f"Observation: {obs}",
            "",
        ]
    return "\n".join(lines)


def parse_action(text: str) -> Tuple[str | None, str | None]:
    """只解析第一轮 Thought/Action，忽略同条回复里后续的轮次或 Final Answer。"""
    action = None
    action_input = None
    seen_thought = False
    for line in text.splitlines():
        if line.startswith("Final Answer:"):
            break
        if line.startswith("Thought:"):
            if seen_thought:
                break
            seen_thought = True
        if line.startswith("Action:"):
            action = line.split("Action:", 1)[1].strip()
        if line.startswith("Action Input:"):
            action_input = line.split("Action Input:", 1)[1].strip()
    return action, action_input
