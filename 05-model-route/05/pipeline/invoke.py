import sys
from pathlib import Path
from typing import Callable, Dict

from .billing import BillingLedger
from .fallback import LLMResult, fallback_invoke
from .router import route_by_complexity

# 复用 01 熔断 + 重试
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "01"))
from breaker import CircuitBreaker, call_with_breaker_and_retry  # noqa: E402


def invoke_with_pipeline(
    user_msg: str,
    complexity: str,
    providers: Dict[str, Callable[[str], dict]],
    breaker: CircuitBreaker,
    ledger: BillingLedger,
    max_retries: int = 2,
) -> LLMResult:
    """闭环：路由 → 熔断 → 重试 → 降级 → 计费。"""
    decision = route_by_complexity(complexity)
    primary_fn = providers[decision.model]

    def _call():
        return primary_fn(user_msg)

    try:
        raw = call_with_breaker_and_retry(_call, breaker, max_retries=max_retries)
        result = LLMResult(
            text=raw["text"],
            model=decision.model,
            prompt_tokens=raw["prompt_tokens"],
            completion_tokens=raw["completion_tokens"],
        )
    except Exception:
        result = fallback_invoke(user_msg, decision.model, providers)

    ledger.record(
        result.model,
        result.prompt_tokens,
        result.completion_tokens,
        degraded=result.degraded,
    )
    return result
