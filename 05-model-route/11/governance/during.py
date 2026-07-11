from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GenerationCheck:
    allowed: bool
    reason: str
    answer: Optional[str] = None


def check_during(
    answer: str,
    sources: List[str],
    min_citations: int = 1,
    min_confidence: float = 0.5,
    confidence: float = 0.8,
) -> GenerationCheck:
    """事中：要求引用来源；低置信度拒答。"""
    if confidence < min_confidence:
        return GenerationCheck(False, "confidence_below_threshold")
    cited = sum(1 for sid in sources if sid in answer)
    if cited < min_citations:
        return GenerationCheck(False, "missing_citation")
    return GenerationCheck(True, "ok", answer=answer)


def refuse(reason: str) -> str:
    messages = {
        "confidence_below_threshold": "置信度不足，无法可靠回答。",
        "missing_citation": "未找到可引用依据，拒绝生成。",
        "no_retrieval": "知识库无相关内容，请换个问法或联系人工。",
    }
    return messages.get(reason, "无法回答。")
