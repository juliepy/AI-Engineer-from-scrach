from typing import Callable, List


def _parse_candidate_lines(text: str, k: int) -> List[str]:
    lines: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        for prefix in ("- ", "* ", "1. ", "2. ", "3. "):
            if line.startswith(prefix):
                line = line[len(prefix) :].strip()
        lines.append(line)
    return lines[:k]


def expand_candidates(
    state: str,
    llm: Callable[[str], str],
    k: int = 3,
    tool_names: List[str] | None = None,
) -> List[str]:
    """Expand：由 LLM 生成 k 个不同的候选下一步。"""
    from agent.prompt import build_expand_prompt

    names = tool_names or ["calculator", "word_count", "get_current_time"]
    prompt = build_expand_prompt(state, k, names)
    text = llm(prompt)
    candidates = _parse_candidate_lines(text, k)
    if not candidates:
        candidates = [
            "Action: calculator[21+21]",
            "Thought: 先计算再统计字符数",
            "Action: word_count[42]",
        ][:k]
    return candidates
