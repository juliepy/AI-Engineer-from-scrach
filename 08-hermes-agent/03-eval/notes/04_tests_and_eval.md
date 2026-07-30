# 04 · 三份契约测试跟 Eval 什么关系

> 讲解顺序：[`README.md`](./README.md) · **桥** · 上一篇 [`03`](./03_eval_harness.md)  
> 延伸：[`05`](./05_test_prompt_caching.md) · [`06`](./06_test_context_compressor.md) · [`07`](./07_test_memory_provider.md) · 主线 [`01`](./01_eval_invariants.md)

---

## 0. 一句话

**它们不是 Eval 流水线里的一步，而是 Eval 要学的「测什么 / 怎么测」的真仓范例。**

---

## 1. 总览图

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    subgraph Runtime["Runtime 行为（会被砸缓存 / 改上下文）"]
        PC["prompt_caching"]
        CC["context_compressor"]
        MP["memory_provider"]
    end

    subgraph Tests["真仓契约测试（课堂范例）"]
        T1["test_prompt_caching.py"]
        T2["test_context_compressor.py"]
        T3["test_memory_provider.py"]
    end

    subgraph Eval["03-eval 在做什么"]
        INV["① 不变量心智<br/>测关系不测快照"]
        TRACE["② 冻结 Trace 上的同款契约<br/>system 稳 / role / tools"]
        HAR["③ Harness 打分 + RCA"]
    end

    PC --> T1
    CC --> T2
    MP --> T3
    T1 --> INV
    T2 --> INV
    T3 --> INV
    INV --> TRACE --> HAR
    Runtime -.->|违反契约时| TRACE

    style Runtime fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style Tests fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style Eval fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style PC fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style CC fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style MP fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style T1 fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style T2 fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style T3 fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style INV fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style TRACE fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style HAR fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
```

---

## 2. 对照表

| 关系 | 说明 |
|------|------|
| **哲学同源** | AGENTS.md「Behavior contracts over snapshots」——三份测试是正面教材；`01` 直接拿它们举例 |
| **不是 Eval 入口** | Eval demo 跑 `run_eval_suite.py` / Layer A，**不会**拿这三份当打分器 |
| **解释「为什么要评这些」** | Eval 查 system 稳、role 交替、tools 不中途变——正因 caching / 压缩 / memory 一乱就会砸前缀或毁布局 |
| **分工** | 单元测试：改源码立刻红；Eval：对整条冻结 loop 轨迹打分 + RCA |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    UT["单元契约测试<br/>test_prompt_caching 等"] --> FAST["改一行立刻红<br/>模块级"]
    EV["Eval Harness<br/>冻结 Trace 打分"] --> SLOW["整条轨迹行为分<br/>+ RCA"]

    style UT fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style FAST fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style EV fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style SLOW fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
```

---

## 3. 不变量怎么映射到 Eval check

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"14px"}}}%%
flowchart TB
    PC2["prompt_caching<br/>前缀稳定 / ≤4 断点"] --> S["Eval: system_stable"]
    CC2["context_compressor<br/>唯一合法改历史"] --> R["Eval: role / 压缩后仍可完成任务"]
    MP2["memory_provider<br/>别每轮重建 system"] --> S
    PC2 --> T["Eval: tools 足迹不中途变"]

    style PC2 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style CC2 fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style MP2 fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style S fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style R fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style T fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

| Runtime / 测试讲稿 | Eval 侧对应信号 |
|--------------------|-----------------|
| [`05` prompt caching](./05_test_prompt_caching.md) | `system_stable`、中途不改 toolset |
| [`06` compressor](./06_test_context_compressor.md) | 压缩是改历史的例外；压缩后仍要 role 合法 |
| [`07` memory](./07_test_memory_provider.md) | system 静态块会话级稳定 |

---

## 4. 建议读法

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    A["① 01→02→03<br/>Eval 在干什么"] --> B["② 本文关系图"]
    B --> C["③ 05→06→07<br/>契约长什么样"]

    style A fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style B fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style C fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

下一步：[`05_test_prompt_caching.md`](./05_test_prompt_caching.md)。
