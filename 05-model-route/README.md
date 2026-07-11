# 05-model-route：模型路由与工程化实践

教材代码 + 面试清单对照。每目录可独立运行：`cd 0X && python main.py`（`04` 用 `pytest -v`）。

## 面试清单 ↔ 代码

| 清单项 | 目录 | 要点 |
|--------|------|------|
| 路由 → 熔断 → 重试 → 降级 → 计费闭环 | `01` + `05` | `01` 熔断/退避；`05/pipeline/invoke.py` 串起全链 |
| Closed / Open / Half-Open 与探测流量 | `01` | `half_open_max_calls`、`success_threshold` |
| Token 估算 vs 账单对账差异 | `02` + `06` | `02` tiktoken；`06` 估算 diff 告警 |
| Trace 应挂的 Span 类型 | `07` | `SpanKind`：route / llm / tool / cache / breaker / retry / fallback / billing |
| 工具调用权限与校验分层 | `08` + `04` | 白名单 → Schema → 审计；`04` Mock 集成测 |
| 金丝雀 vs 蓝绿适用场景 | `09` | 10% 流量金丝雀 vs 整包蓝绿切换 |
| L1/L2 缓存与语义缓存风险 | `03` + `02` + `10` | `03` 双层；`10` 精确 vs 语义误命中 |
| 幻觉治理事前—事中—事后 | `11` | RAG grounding → Citation 拒答 → 反馈审计 |

## 目录一览

| 目录 | 主题 |
|------|------|
| `01` | 熔断器 + 指数退避重试 |
| `02` | tiktoken + 请求指纹精确缓存 |
| `03` | 异步 + 信号量 + L1/L2 缓存 |
| `04` | pytest + Mock LLM 集成测试 |
| `05` | **闭环**：路由 → 熔断 → 重试 → 降级 → 计费 |
| `06` | Token 估算 vs usage 对账 |
| `07` | Trace Span 类型示意 |
| `08` | 工具白名单 + Schema + 审计 |
| `09` | 金丝雀分流 + 蓝绿切换 |
| `10` | 语义缓存风险演示 |
| `11` | 幻觉三层治理 |

## 闭环示意

```
请求 → route.decision → breaker.allow?
         ↓ 否 → fallback → billing
         ↓ 是 → retry + llm.chat
              ↓ 失败 → fallback → billing
              ↓ 成功 → billing
```

## 运行

```bash
cd 05-model-route/05 && python main.py
cd 05-model-route/06 && python main.py
cd 05-model-route/04 && pytest -v
```

可选依赖：`pip install tiktoken`（`02`）、`pip install pytest`（`04`）。
