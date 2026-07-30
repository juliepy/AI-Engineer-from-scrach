# 07 · `test_memory_provider.py` 讲解

> 讲解顺序：[`README.md`](./README.md) · **范例 3/3** · 上一篇 [`06`](./06_test_context_compressor.md)  
> 源码：`agent/memory_provider.py`（ABC）+ `agent/memory_manager.py`（编排）  
> 测试：`hermes_src/tests/agent/test_memory_provider.py`（~1590 行）  
> 定位：可插拔记忆后端的 **契约 + Manager 编排**，不是某个具体 SaaS 的实现细节  
> 跟 Eval：[`04_tests_and_eval.md`](./04_tests_and_eval.md) · 目录：[`README.md`](./README.md)

---

## 0. 一句话

`MemoryProvider` 定义记忆插件必须实现的生命周期；`MemoryManager` 是 `run_agent` 的唯一接入点——**最多一个外部 provider**，避免 tool schema 膨胀和互相打架。

---

## 1. 它在热路径的哪一步

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"16px"},"themeCSS":".edgeLabel,.edgeLabel p,.edgeLabel span{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart TB
    subgraph Session["会话生命周期"]
        INIT["initialize(session_id)"] --> SP["system_prompt_block()<br/>写入 system 静态段"]
    end

    subgraph EachTurn["每一轮"]
        PF["prefetch(query)<br/>注入相关记忆"] --> LOOP["Agent Loop<br/>思考 / 工具"]
        LOOP --> SYNC["sync_turn(user, asst)"]
        SYNC --> QPF["queue_prefetch<br/>为下一轮预热"]
    end

    subgraph Special["特殊事件"]
        COMP["on_pre_compress<br/>压缩前提取"]
        END["on_session_end"]
        WRITE["on_memory_write<br/>镜像内置 memory 写入"]
        SHUT["shutdown()"]
    end

    Session --> EachTurn
    LOOP -.->|上下文将爆| COMP
    EachTurn --> END
    END --> SHUT

    style Session fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style EachTurn fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style Special fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style INIT fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style SP fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style PF fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
    style LOOP fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style SYNC fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
    style QPF fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style COMP fill:#F48FB1,stroke:#880E4F,stroke-width:2px,color:#111111
    style END fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style WRITE fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style SHUT fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
```

和另外两个模块的关系：

| 模块 | 关系 |
|------|------|
| Prompt Caching | 记忆写入 system **会话开始时**；中途别重建 system，否则砸缓存 |
| Context Compressor | 压缩前走 `on_pre_compress`，把要留的抽进记忆/摘要 |

---

## 2. 架构：ABC + Manager + 插件目录

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart TB
    RA["run_agent.AIAgent"] --> MM["MemoryManager"]

    MM --> BUILTIN["builtin<br/>（可选）"]
    MM --> EXT["最多 1 个 external<br/>honcho / mem0 / …"]

    EXT --> DISC["发现路径"]
    DISC --> P1["plugins/memory/&lt;name&gt;/"]
    DISC --> P2["~/.hermes/plugins/"]
    DISC --> P3["pip entry points"]

    MM --> TOOLS["inject_memory_provider_tools<br/>规范化 schema → 注册"]

    style RA fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style MM fill:#FFD54F,stroke:#F57F17,stroke-width:2px,color:#111111
    style BUILTIN fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style EXT fill:#FFAB91,stroke:#BF360C,stroke-width:2px,color:#111111
    style TOOLS fill:#B39DDB,stroke:#4527A0,stroke-width:2px,color:#111111
    style DISC fill:#80DEEA,stroke:#006064,stroke-width:2px,color:#111111
    style P1 fill:#B2EBF2,stroke:#00838F,stroke-width:2px,color:#111111
    style P2 fill:#B2EBF2,stroke:#00838F,stroke-width:2px,color:#111111
    style P3 fill:#B2EBF2,stroke:#00838F,stroke-width:2px,color:#111111
```

硬规则（测试 `test_second_external_rejected`）：

```text
providers ⊆ { builtin?,  exactly_one_external? }
第二个 external → 拒绝并告警，不静默双开
```

---

## 3. Provider 生命周期（Fake 也能跑通）

测试用 `FakeMemoryProvider` 记录每次调用，断言 Manager **转发顺序与合并行为**。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","actorTextColor":"#111111","actorBkg":"#BBDEFB","actorBorder":"#0D47A1","actorLineColor":"#90CAF9","noteBkgColor":"#FFE082","noteTextColor":"#111111","noteBorderColor":"#F57F17","signalColor":"#90CAF9","signalTextColor":"#FFFFFF","labelTextColor":"#FFFFFF","sequenceNumberColor":"#FFFFFF","fontSize":"15px"}}}%%
sequenceDiagram
    participant Agent
    participant Mgr as MemoryManager
    participant P as FakeMemoryProvider

    Agent->>Mgr: add_provider(P)
    Agent->>Mgr: initialize_all(session_id)
    Mgr->>P: initialize(...)

    Note over Agent,P: 每轮开始
    Agent->>Mgr: prefetch_all(query)
    Mgr->>P: prefetch(query)
    P-->>Mgr: "Memory from …"
    Mgr-->>Agent: 合并后的 context 文本

    Note over Agent,P: 模型可能调 memory 工具
    Agent->>Mgr: handle_tool_call(name, args)
    Mgr->>P: handle_tool_call(...)

    Note over Agent,P: 每轮结束
    Agent->>Mgr: sync_all(user, asst)
    Mgr->>P: sync_turn(...)
    Agent->>Mgr: queue_prefetch_all(query)
    Mgr->>P: queue_prefetch(...)

    Note over Agent,P: 压缩前 / 会话结束
    Agent->>Mgr: on_pre_compress(messages)
    Mgr->>P: on_pre_compress(...)
    Agent->>Mgr: shutdown_all()
    Mgr->>P: shutdown()
```

---

## 4. Tool Schema 规范化（防整盘工具挂掉）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"16px"},"themeCSS":".edgeLabel,.edgeLabel p,.edgeLabel span{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart LR
    IN["get_tool_schemas()"] --> N["normalize_tool_schema()"]
    N -->|裸函数 schema| OK["{name, description, parameters}"]
    N -->|已包一层 OpenAI tool| UNWRAP["解开 function 层"]
    UNWRAP --> OK
    N -->|无 name / 畸形| DROP["返回 None<br/>跳过并告警"]

    OK --> REG["注入 toolset"]
    DROP --> SKIP["不加入 tools[]"]

    style IN fill:#81D4FA,stroke:#01579B,stroke-width:2px,color:#111111
    style N fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style OK fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style UNWRAP fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style DROP fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style REG fill:#AED581,stroke:#33691E,stroke-width:2px,color:#111111
    style SKIP fill:#B0BEC5,stroke:#37474F,stroke-width:2px,color:#111111
```

背景：某个 provider 若返回「已经 wrap 过的」schema，再 wrap 一次会变成无顶层 `name` → DeepSeek 等直接 **整请求 400**，整盘工具失效（#47707）。测试覆盖：

- `TestNormalizeToolSchema`
- `TestMemoryInjectionRejectsMalformedSchema`

---

## 5. 测试结构地图

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","primaryColor":"#BBDEFB","primaryBorderColor":"#0D47A1","lineColor":"#90CAF9","fontSize":"15px"}}}%%
mindmap
  root((test_memory_provider))
    ABC 契约
      TestMemoryProviderABC
      FakeMemoryProvider
    Manager 编排
      TestMemoryManager
      合并 prompt / prefetch
      单 external 限制
    插件发现
      TestPluginMemoryDiscovery
      TestUserInstalledProviderDiscovery
      TestUserInstalledProviderCli
    工具与门控
      TestSequentialDispatchRouting
      TestMemoryToolToolsetGate
      TestContextEngineToolsetGate
      TestNormalizeToolSchema
    上下文安全
      TestMemoryContextFencing
      TestFlattenMessageContent
      TestCommitMemorySessionRouting
      TestOnMemoryWriteBridge
    其他
      TestSetupFieldFiltering
      TestHonchoCadenceTracking
```

| 测试类 | 核心断言 |
|--------|----------|
| `TestMemoryProviderABC` | 不能直接实例化 ABC；可选钩子默认 no-op |
| `TestMemoryManager` | 增删、合并 prompt/prefetch、拒第二个 external |
| `Test*Discovery` | 内置 / 用户安装 / CLI 注册路径 |
| `TestMemoryContextFencing` | 注入记忆有边界，避免污染角色交替 |
| `Test*ToolsetGate` | 未开 toolset 时不暴露 memory 工具 |
| `TestOnMemoryWriteBridge` | 内置 memory 写入可镜像给外部 provider |

---

## 6. 与「别砸 Prompt Cache」的契约

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart TB
    BAD["❌ 每轮重建 system<br/>塞进最新 prefetch"] --> CACHE_BREAK["前缀变化<br/>缓存全废"]
    GOOD["✅ system 静态块会话级稳定<br/>prefetch 走独立注入通道"] --> CACHE_OK["前缀可复用"]

    style BAD fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style CACHE_BREAK fill:#E57373,stroke:#B71C1C,stroke-width:2px,color:#111111
    style GOOD fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style CACHE_OK fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
```

`system_prompt_block()` = 静态说明；动态 recall 走 `prefetch()`，由 Manager / Agent 按既定通道注入，而不是每轮改写 system 字节。

---

## 7. 面试话术

> Hermes 记忆层是窄腰：`MemoryProvider` ABC + `MemoryManager` 单点编排。  
> 产品上可以接很多后端，但**同时只跑一个 external**；新后端应做独立插件仓库，不往 core 塞。  
> 测试用 Fake provider 验生命周期与 schema 规范化，不绑死「今天 catalog 里有几个模型」。

---

## 8. 怎么跑

```bash
scripts/run_tests.sh tests/agent/test_memory_provider.py
scripts/run_tests.sh tests/agent/test_memory_provider.py::TestMemoryManager
```

相关讲稿：[`05`](./05_test_prompt_caching.md)（缓存断点）· [`06`](./06_test_context_compressor.md)（压缩与 `on_pre_compress`）· 目录 [`README.md`](./README.md)。
