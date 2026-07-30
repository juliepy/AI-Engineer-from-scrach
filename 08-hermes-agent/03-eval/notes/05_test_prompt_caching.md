# 05 · `test_prompt_caching.py` 讲解

> 讲解顺序：[`README.md`](./README.md) · **范例 1/3** · 上一篇 [`04`](./04_tests_and_eval.md)  
> 源码：`hermes_src/agent/prompt_caching.py`  
> 测试：`hermes_src/tests/agent/test_prompt_caching.py`（~226 行）  
> 策略名：`system_and_3` — 最多 **4** 个 `cache_control` 断点  
> 跟 Eval：[`04_tests_and_eval.md`](./04_tests_and_eval.md) · 下一篇 [`06`](./06_test_context_compressor.md)

---

## 0. 一句话

给 Anthropic 请求打 **Prompt Cache 断点**：system + 最近 3 条可承载标记的非 system 消息，让多轮对话复用前缀，输入成本约降 75%。测试断言的是「标记怎么挂才合法」，不是「今天有哪些模型」。

---

## 1. 它在 Agent 热路径的哪一步

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart LR
    subgraph Prep["Turn 组装"]
        A["messages<br/>system + history"] --> B["apply_anthropic_cache_control()"]
    end

    B --> C["带 cache_control<br/>的 API payload"]
    C --> D["provider API"]

    subgraph Cache["Provider 侧"]
        D --> E{"前缀命中?"}
        E -->|命中| F["读缓存<br/>便宜"]
        E -->|未命中| G["全量计费<br/>写入缓存"]
    end

    style Prep fill:#BBDEFB,stroke:#0D47A1,stroke-width:2px,color:#111111
    style Cache fill:#C8E6C9,stroke:#1B5E20,stroke-width:2px,color:#111111
    style A fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#111111
    style B fill:#FFE0B2,stroke:#E65100,stroke-width:2px,color:#111111
    style C fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#111111
    style D fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#111111
    style E fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#111111
    style F fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style G fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
```

- **不改**历史内容、不换 toolset、不重建 system —— 只在**发送前**深拷贝并打标记。
- 这是 AGENTS.md「Prompt Caching Must Not Break」的配套实现：缓存靠前缀字节稳定；本模块负责断点落在哪。

---

## 2. `system_and_3` 策略

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart TB
    M0["system ⭐ breakpoint #1"]
    M1["user msg1"]
    M2["assistant msg2 ⭐"]
    M3["user msg3 ⭐"]
    M4["assistant msg4 ⭐"]

    M0 --- M1 --- M2 --- M3 --- M4

    note["最多 4 个断点：<br/>system + 末尾 3 条<br/>可承载 marker 的非 system"]

    style M0 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style M1 fill:#CFD8DC,stroke:#37474F,stroke-width:2px,color:#111111
    style M2 fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style M3 fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style M4 fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style note fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
```

| 规则 | 含义 |
|------|------|
| `breakpoints ≤ 4` | Anthropic 协议上限（不变量，不是快照） |
| TTL `5m` / `1h` | 同一会话内复用；`1h` 时 marker 带 `"ttl": "1h"` |
| Deep copy | 原 `messages` 不被原地污染 |

---

## 3. Native Anthropic vs OpenRouter（核心差异）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart TB
    START["_apply_cache_marker(msg)"] --> Q{"native_anthropic?"}

    Q -->|True| NA["顶层 msg.cache_control = marker<br/>适配器再挪进 content"]
    Q -->|False| OR["_can_carry_marker?<br/>只认 content part"]

    OR -->|空 assistant / 空 tool| SKIP["跳过<br/>避免 hang / 浪费断点"]
    OR -->|有文本| WRAP["string → list[{text, cache_control}]<br/>list → 标最后一项"]

    style START fill:#81D4FA,stroke:#01579B,stroke-width:2px,color:#111111
    style Q fill:#FFF59D,stroke:#F57F17,stroke-width:2px,color:#111111
    style NA fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style OR fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style SKIP fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style WRAP fill:#AED581,stroke:#33691E,stroke-width:2px,color:#111111
```

| 路径 | tool 空内容 | assistant 空（纯 tool_calls） | 非空 tool |
|------|-------------|-------------------------------|-----------|
| Native Anthropic | 可顶层打标 | 可顶层打标 | 顶层打标 |
| OpenRouter | **跳过** | **跳过** | 包进 content part 再打标 |

测试里反复强调：OpenRouter 对 `role:tool` 顶层 `cache_control` 会 **silent hang**。

---

## 4. 测试结构地图

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","primaryColor":"#BBDEFB","primaryBorderColor":"#0D47A1","lineColor":"#90CAF9","fontSize":"15px"}}}%%
mindmap
  root((test_prompt_caching))
    TestApplyCacheMarker
      tool 顶层 / content part
      空 assistant 跳过
      string / list / 空 list
    TestCanCarryMarker
      native 永远 True
      OpenRouter 空内容 False
      list 末项必须是 dict
    TestApplyAnthropicCacheControl
      深拷贝
      system + last 3
      ≤ 4 breakpoints
      TTL 1h
      tool loop 不浪费断点
```

| 测试类 | 测什么 |
|--------|--------|
| `TestApplyCacheMarker` | 单条消息怎么挂标记 |
| `TestCanCarryMarker` | 这条消息能不能占用一个断点槽 |
| `TestApplyAnthropicCacheControl` | 整条策略：拷贝、system、末尾 3、上限 4、TTL |

---

## 5. 典型不变量（面试可背）

```text
1. cache breakpoints ≤ 4
2. OpenRouter：空 assistant / 空 tool 不消耗断点
3. OpenRouter：非空 tool 的 marker 必须在 content part，不能在顶层
4. apply_* 返回深拷贝，输入 messages 不变
5. _can_carry_marker 与 _apply_cache_marker 对 list 末项规则一致
   （否则 gate 通过但没打上 → 浪费断点）
```

---

## 6. 怎么跑

```bash
# 真仓库（CI 同款）
scripts/run_tests.sh tests/agent/test_prompt_caching.py

# 课堂剪枝树仅作阅读；不要冒充 CI
```

下一步：[`06_test_context_compressor.md`](./06_test_context_compressor.md)（超长上下文真正改历史的唯一合法路径）。
