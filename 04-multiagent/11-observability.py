# =============================================================================
#  生产可观测：步数 / Token 估算 / 耗时 Trace
# =============================================================================
#
#  生产难点「钱、慢、死循环、错、看不清」—— 可观测补「看不清」：
#  结构化记录每步 Agent、输入输出长度、耗时，便于成本归因与排障。
#  （Token 用 len/4 粗估；生产应对接真实 usage 与 OpenTelemetry。）
#
# =============================================================================

import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class Span:
    agent: str
    step: int
    input_chars: int
    output_chars: int
    latency_ms: float
    est_tokens: int


@dataclass
class Trace:
    goal: str
    spans: List[Span] = field(default_factory=list)

    def add(self, span: Span) -> None:
        self.spans.append(span)

    def summary(self) -> Dict[str, Any]:
        total_tokens = sum(s.est_tokens for s in self.spans)
        total_ms = sum(s.latency_ms for s in self.spans)
        return {
            "steps": len(self.spans),
            "est_tokens": total_tokens,
            "latency_ms": round(total_ms, 2),
            "est_cost_usd": round(total_tokens / 1_000_000 * 3.0, 6),  # 示意单价
        }


def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def traced_run(
    goal: str,
    agents: List[str],
    agent_fn: Callable[[str, List[str]], str],
) -> Trace:
    trace = Trace(goal=goal)
    context: List[str] = []
    for step, agent in enumerate(agents, 1):
        inp = context + [f"GOAL: {goal}"]
        inp_text = "\n".join(inp)
        t0 = time.perf_counter()
        out = agent_fn(agent, inp)
        elapsed = (time.perf_counter() - t0) * 1000
        tokens = est_tokens(inp_text) + est_tokens(out)
        trace.add(
            Span(
                agent=agent,
                step=step,
                input_chars=len(inp_text),
                output_chars=len(out),
                latency_ms=round(elapsed, 2),
                est_tokens=tokens,
            )
        )
        context.append(f"[{agent}] {out}")
    return trace


def mock_agent(name: str, ctx: List[str]) -> str:
    time.sleep(0.05)  # 模拟 LLM 延迟
    canned = {
        "pm": "用户故事已澄清",
        "dev": "API 已实现",
        "qa": "测试通过 DONE",
    }
    return canned.get(name, f"{name} 完成")


def print_trace(trace: Trace) -> None:
    print(f"目标: {trace.goal}")
    for s in trace.spans:
        print(
            f"  step={s.step} agent={s.agent} "
            f"in={s.input_chars} out={s.output_chars} "
            f"~tokens={s.est_tokens} latency={s.latency_ms}ms"
        )
    print("汇总:", trace.summary())


if __name__ == "__main__":
    print("=== 多 Agent Trace（可观测示意）===")
    tr = traced_run(
        "交付登录 API",
        ["pm", "dev", "qa"],
        mock_agent,
    )
    print_trace(tr)
