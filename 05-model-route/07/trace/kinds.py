from enum import Enum


class SpanKind(str, Enum):
    ROUTE = "route.decision"
    LLM = "llm.chat"
    TOOL = "tool.invoke"
    CACHE = "cache.lookup"
    BREAKER = "breaker.state"
    RETRY = "retry.attempt"
    FALLBACK = "fallback.invoke"
    RETRIEVE = "retrieve"
    BILLING = "billing.record"
