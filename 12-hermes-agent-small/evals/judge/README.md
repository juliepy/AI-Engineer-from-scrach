# LLM-as-judge evals

跑一轮 Waku，再用**同一套 provider**发一条打分 prompt，看回复够不够好（0–10，阈值 6）。

和 `evals/deterministic/`（0/1）**不混用**。也别和 `waku/ops/judge.py`（Compare 竞技场裁判）搞混。

## 怎么跑

```bash
uv run python -m pytest -q evals/judge
# 单个 case
uv run python -m pytest -q evals/judge/test_response_quality.py::test_scheduling_reply_is_helpful -v
```

无当前 provider 的 API key 时整套 skip。

## Case

| 测试 | 在测什么 |
|------|----------|
| `test_scheduling_reply_is_helpful` | 约咖啡回复是否直接、确认动作、简洁 |
| `test_reply_uses_remembered_preference` | 是否用上「Alex 喜欢早会」 |

流程：`respond` → `_judge(prompt)` → `score >= 6`。没有 DeepEval，就是一段 prompt + JSON。
