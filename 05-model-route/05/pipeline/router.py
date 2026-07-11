from dataclasses import dataclass


@dataclass
class RouteDecision:
    model: str
    reason: str


def route_by_complexity(complexity: str) -> RouteDecision:
    """按任务复杂度路由模型（成本 vs 能力）。"""
    table = {
        "simple": RouteDecision("gpt-4o-mini", "简单问答，走低成本模型"),
        "medium": RouteDecision("gpt-4o", "中等推理，走标准模型"),
        "hard": RouteDecision("gpt-4o-pro", "复杂任务，走高能力模型"),
    }
    return table.get(complexity, RouteDecision("gpt-4o-mini", "未知复杂度，默认 mini"))
