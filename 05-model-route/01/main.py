# =============================================================================
#  1.5 简易熔断器 + 指数退避（模型路由 / 下游调用保护）
# =============================================================================
#
#  熔断三态：CLOSED → OPEN → HALF_OPEN → CLOSED
#  - CLOSED：正常放行，累计失败达阈值则跳闸
#  - OPEN：拒绝请求，等待 open_seconds 后进入半开
#  - HALF_OPEN：限量探测，连续成功则闭合，失败则再次跳闸
#
#  重试策略：指数退避 + 随机 jitter，避免惊群
#
# =============================================================================

import sys

from breaker import CircuitBreaker, State, call_with_breaker_and_retry

sys.stdout.reconfigure(encoding="utf-8")


def flaky_model_call(fail_times: int):
    """模拟前 fail_times 次失败、之后成功的下游调用。"""
    state = {"calls": 0}

    def _call():
        state["calls"] += 1
        if state["calls"] <= fail_times:
            raise ConnectionError(f"upstream error #{state['calls']}")
        return {"ok": True, "calls": state["calls"]}

    return _call


if __name__ == "__main__":
    breaker = CircuitBreaker(
        failure_threshold=3,
        success_threshold=2,
        open_seconds=2.0,
        half_open_max_calls=2,
    )

    print("=== 场景 1：偶发失败，重试后成功 ===")
    result = call_with_breaker_and_retry(flaky_model_call(2), breaker, max_retries=3)
    print(f"  结果: {result}  熔断器状态: {breaker.state.name}")
    print()

    print("=== 场景 2：连续失败触发熔断 ===")
    breaker2 = CircuitBreaker(failure_threshold=2, open_seconds=1.0)
    try:
        call_with_breaker_and_retry(flaky_model_call(99), breaker2, max_retries=2)
    except ConnectionError as e:
        print(f"  最终异常: {e}")
    print(f"  熔断器状态: {breaker2.state.name}（应为 OPEN）")
    print()

    print("=== 场景 3：熔断打开期间直接拒绝 ===")
    try:
        call_with_breaker_and_retry(flaky_model_call(0), breaker2, max_retries=1)
    except RuntimeError as e:
        print(f"  拒绝原因: {e}")
