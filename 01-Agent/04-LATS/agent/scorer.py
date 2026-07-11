import re
from typing import Callable

from agent.prompt import build_llm_score_prompt
from agent.types import Scorer


def heuristic_scorer(state: str, action: str) -> float:
    """廉价启发式：根据动作与任务关键词给分。"""
    text = (state + "\n" + action).lower()
    score = 0.2
    if "calculator" in action or "21+21" in action:
        score += 0.35
    if "word_count" in action:
        score += 0.35
    if "42" in text:
        score += 0.1
    if "字符" in state or "字符" in action:
        if "word_count" in action:
            score += 0.15
    if "get_current_time" in action and ("21+21" in state or "字符" in state):
        score -= 0.2
    return min(1.0, max(0.0, score))


def make_llm_scorer(llm: Callable[[str], str]) -> Scorer:
    """用 LLM 对单步候选打分（Simulate 的一种）。"""

    def score(state: str, action: str) -> float:
        raw = llm(build_llm_score_prompt(state, action))
        match = re.search(r"0?\.\d+|1\.0|1|0", raw)
        if not match:
            return heuristic_scorer(state, action)
        try:
            return min(1.0, max(0.0, float(match.group())))
        except ValueError:
            return heuristic_scorer(state, action)

    return score


def combined_scorer(heuristic: Scorer, llm: Scorer | None = None, llm_weight: float = 0.3) -> Scorer:
    if llm is None:
        return heuristic

    def score(state: str, action: str) -> float:
        h = heuristic(state, action)
        l = llm(state, action)
        return (1 - llm_weight) * h + llm_weight * l

    return score


def score_action(state: str, action: str, scorer: Scorer) -> float:
    return scorer(state, action)
