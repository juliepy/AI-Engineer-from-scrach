# =============================================================================
#  Trace Span 类型（OpenTelemetry 风格示意）
# =============================================================================

import sys
import time
import uuid

from trace import SpanKind, Trace

sys.stdout.reconfigure(encoding="utf-8")


def demo_request(goal: str) -> Trace:
    tr = Trace(trace_id=uuid.uuid4().hex[:12], goal=goal)

    s = tr.start_span(SpanKind.ROUTE, "pick_model").set_attr("complexity", "medium")
    time.sleep(0.01)
    s.set_attr("model", "gpt-4o").end()

    s = tr.start_span(SpanKind.CACHE, "exact_cache").set_attr("key", "abc123")
    time.sleep(0.005)
    s.set_attr("hit", False).end()

    s = tr.start_span(SpanKind.BREAKER, "allow_call").set_attr("state", "CLOSED")
    time.sleep(0.005)
    s.end()

    for attempt in range(2):
        s = tr.start_span(SpanKind.RETRY, f"attempt_{attempt}")
        time.sleep(0.02)
        s.set_attr("backoff_sec", 0.5 * (2**attempt)).end()

    s = tr.start_span(SpanKind.LLM, "chat_completion")
    time.sleep(0.05)
    s.set_attr("model", "gpt-4o").set_attr("prompt_tokens", 120).set_attr(
        "completion_tokens", 80
    ).end()

    s = tr.start_span(SpanKind.BILLING, "record_usage")
    time.sleep(0.005)
    s.set_attr("cost_usd", 0.001).end()

    return tr


if __name__ == "__main__":
    tr = demo_request("总结本周迭代")
    print(f"=== Trace {tr.trace_id} goal={tr.goal} ===")
    for sp in tr.spans:
        dur = round(sp.end_ms - sp.start_ms, 2)
        print(f"  [{sp.kind.value}] {sp.name} {dur}ms attrs={sp.attributes}")
    kinds = sorted({sp.kind.value for sp in tr.spans})
    print()
    print("本 Trace 挂载 Span 类型:", kinds)
