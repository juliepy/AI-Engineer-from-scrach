from typing import Callable, List

from agent.prompt import build_reflector_prompt, parse_reflection

MAX_REFLECTION_LEN = 400


def reflect(
    task: str,
    output: str,
    feedback: str,
    score: float,
    reflections: List[str],
    llm: Callable[[str], str],
) -> str:
    """Reflection：根据评估反馈生成可复用的改进策略文本。"""
    prompt = build_reflector_prompt(task, output, feedback, score, reflections)
    raw = llm(prompt)
    text = parse_reflection(raw)
    if len(text) > MAX_REFLECTION_LEN:
        text = text[:MAX_REFLECTION_LEN] + "..."
    return text


def trim_reflections(
    reflections: List[str],
    max_items: int = 5,
    max_chars_per_item: int = 400,
) -> List[str]:
    """限制条数与长度，只保留最近的高信息密度条目。"""
    trimmed = [r[:max_chars_per_item] for r in reflections[-max_items:]]
    seen: set[str] = set()
    deduped: List[str] = []
    for r in reversed(trimmed):
        key = r[:80].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    deduped.reverse()
    return deduped
