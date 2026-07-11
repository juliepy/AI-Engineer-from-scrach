# =============================================================================
#  闭环示例：路由 → 熔断 → 重试 → 降级 → 计费
# =============================================================================

import sys

sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[1] / "01")
from breaker import CircuitBreaker  # noqa: E402

from pipeline import BillingLedger, invoke_with_pipeline, route_by_complexity

sys.stdout.reconfigure(encoding="utf-8")


def mock_provider(model: str, fail: bool = False):
    def _fn(msg: str) -> dict:
        if fail:
            raise ConnectionError(f"{model} unavailable")
        return {
            "text": f"[{model}] 回答: {msg[:20]}",
            "prompt_tokens": len(msg) // 4 + 5,
            "completion_tokens": 30,
        }

    return _fn


if __name__ == "__main__":
    ledger = BillingLedger()
    providers = {
        "gpt-4o-pro": mock_provider("gpt-4o-pro", fail=True),
        "gpt-4o": mock_provider("gpt-4o"),
        "gpt-4o-mini": mock_provider("gpt-4o-mini"),
    }

    route = route_by_complexity("hard")
    print(f"=== 路由决策: {route.model} ({route.reason}) ===")

    breaker = CircuitBreaker(failure_threshold=2, open_seconds=1.0)
    result = invoke_with_pipeline(
        "解释 Transformer 注意力机制",
        "hard",
        providers,
        breaker,
        ledger,
    )
    print(f"响应: {result.text}")
    print(f"降级: {result.degraded}  模型: {result.model}")
    print(f"账单条目: {ledger.records[-1]}")
    print(f"累计成本 USD: {ledger.total_cost()}")
