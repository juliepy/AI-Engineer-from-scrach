# 02 · Logging / Trace：session_tag 与根因定位

> 讲解顺序：[`README.md`](./README.md) · **主线 2/3** · 上一篇 [`01`](./01_eval_invariants.md)  
> 对照：`../hermes_src/hermes_logging.py`  
> 真源码挂钩：`agent/turn_context.py` → `set_session_context(session_id)`  
> Demo：`../demo/teaching/logging/` · fixtures `sample_agent.log`  
> Golden Trace：`../../02-run-agent/demo/exports/agent_loop/06_trace.md`

---

## 0. 一句话

**Trace 查因果，Metrics 看 SLO，Log 查细节。**  
Hermes 用 `session_tag` 把一条对话串到 `agent.log`；教学 demo 用结构化 `trace[]`（`api_request` / `api_response` / `tool_result` / `loop_exit`）做 RCA。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart LR
    TRACE["Trace<br/>因果链"] --> Q1["第几次 API<br/>选了错工具？"]
    METRICS["Metrics<br/>SLO"] --> Q2["成功率 / P99<br/>成本趋势"]
    LOG["Log<br/>细节"] --> Q3["这个 session<br/>WARNING 原文？"]

    style TRACE fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style METRICS fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style LOG fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style Q1 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style Q2 fill:#E1BEE7,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style Q3 fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
```

---

## 1. 日志分流（读代码）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    HOME["get_hermes_home()/logs/"] --> A["agent.log<br/>INFO+ catch-all"]
    HOME --> E["errors.log<br/>WARNING+ 快 triage"]
    HOME --> G["gateway.log<br/>mode=gateway"]
    HOME --> U["gui.log<br/>mode=gui"]

    style HOME fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style A fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style E fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style G fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style U fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
```

```text
~/.hermes/logs/          # 实际路径走 get_hermes_home()，支持 profile
├── agent.log            # INFO+，catch-all
├── errors.log           # WARNING+，快速 triage
├── gateway.log          # mode=gateway 时：gateway.* / plugins.platforms
└── gui.log              # mode=gui 时：dashboard / tui_gateway / uvicorn
```

按 **logger 名前缀** 分流到组件（教学摘录）：

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"14px"}}}%%
flowchart LR
    subgraph Pref["COMPONENT_PREFIXES"]
        GW["gateway → gateway.log"]
        AG["agent / run_agent → agent.log"]
        TL["tools → agent.log"]
        CLI["hermes_cli / cli"]
        CR["cron"]
        GUI["web_server / tui / uvicorn → gui.log"]
    end

    style Pref fill:#BBDEFB,stroke:#0D47A1,stroke-width:2px,color:#111111
    style GW fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style AG fill:#90CAF9,stroke:#1565C0,stroke-width:2px,color:#111111
    style TL fill:#90CAF9,stroke:#1565C0,stroke-width:2px,color:#111111
    style CLI fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style CR fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style GUI fill:#B39DDB,stroke:#4527A0,stroke-width:2px,color:#111111
```

```python
COMPONENT_PREFIXES = {
    "gateway": ("gateway", "hermes_plugins", "plugins.platforms"),
    "agent":   ("agent", "run_agent", "model_tools", "batch_runner"),
    "tools":   ("tools",),
    "cli":     ("hermes_cli", "cli"),
    "cron":    ("cron",),
    "gui":     ("hermes_cli.web_server", "hermes_cli.pty_bridge", "tui_gateway", "uvicorn"),
}
```

用户侧：`hermes logs [--follow] [--level …] [--session …] [--component …]`。

---

## 2. session_tag 机制

把「这一轮对话」钉到每一行日志上，才能按 session 过滤。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","actorTextColor":"#111111","actorBkg":"#BBDEFB","actorBorder":"#0D47A1","noteBkgColor":"#FFE082","noteTextColor":"#111111","noteBorderColor":"#F57F17","signalColor":"#90CAF9","signalTextColor":"#111111","fontSize":"14px"}}}%%
sequenceDiagram
    participant Turn as Agent Turn
    participant Ctx as turn_context
    participant Log as LogRecord factory
    participant File as agent.log

    Turn->>Ctx: set_session_context(session_id)
    Note over Ctx: thread-local 存 sid
    Turn->>Log: logger.info(...)
    Log->>Log: 注入 session_tag = " [sid]"
    Log->>File: asctime level [sid] name: message
    Turn->>Ctx: clear_session_context()
```

格式：

```text
%(asctime)s %(levelname)s%(session_tag)s %(name)s: %(message)s
```

要点：用 **Record factory** 而不是只靠 Filter——保证第三方 handler / 子 logger 传播时也不会丢字段（避免 `KeyError: session_tag`）。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    BAD["只靠 Filter"] --> MISS["子 logger / 第三方 handler<br/>可能缺字段 → KeyError"]
    GOOD["Record factory<br/>创建时注入"] --> OK["传播链上始终有<br/>session_tag"]

    style BAD fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style MISS fill:#E57373,stroke:#B71C1C,stroke-width:2px,color:#111111
    style GOOD fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style OK fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
```

---

## 3. Trace vs Log（两套信号）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    LOOP["Agent Loop 热路径"] -.->|旁路| LOG["agent.log 行<br/>session_tag 过滤"]
    LOOP -.->|埋点| TR["trace[] 事件流<br/>可冻结成 JSON"]

    LOG --> QLOG["何时 WARNING？<br/>工具异常原文？"]
    TR --> QTR["第几次 API 错工具？<br/>budget 何时耗尽？<br/>system 是否被改？"]

    style LOOP fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style LOG fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style TR fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style QLOG fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style QTR fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
```

| 信号 | 来源 | 适合问什么 |
|------|------|------------|
| `agent.log` 行 | `hermes_logging` | 某 session 何时报 WARNING？工具抛了啥异常？ |
| `06_trace.md` / `golden_run.json` | demo `conversation_loop` 埋点 | 第几次 API 选了错工具？budget 何时耗尽？system 是否被改？ |

### Loop 内可观测点（对照 `02-run-agent`）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    R1["api_request<br/>tools + roles 摘要"] --> R2["api_response<br/>content / tool_calls"]
    R2 --> R3["tool_result<br/>name + args + result"]
    R3 --> R1
    R2 --> X["loop_exit<br/>reason / budget / interrupt"]

    style R1 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style R2 fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style R3 fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style X fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
```

```text
api_request  → tools schema + message_roles 摘要
api_response → content / tool_calls
tool_result  → name + args + result（可截断）
loop_exit    → reason / budget_used / interrupted
```

---

## 4. 根因分析套路（面试会讲）

给定一条失败 Trace，按序问：

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    S1["① 退出理由？<br/>exhausted / grace / interrupt / 正常"] --> S2["② 工具选对了吗？<br/>期望 ⊆ 实际？空转？"]
    S2 --> S3["③ 上下文病了吗？<br/>system 变？role 连发？"]
    S3 --> S4["④ 预算够吗？<br/>api_calls vs max；grace 浪费？"]
    S4 --> RCA["写出 root_cause + evidence"]

    style S1 fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style S2 fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style S3 fill:#FFF59D,stroke:#F57F17,stroke-width:2px,color:#111111
    style S4 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style RCA fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

1. **退出理由？** `budget_exhausted` / `budget_grace_call` / `interrupt` / 正常文本？  
2. **工具选对了吗？** 期望工具是否出现在 `tool_calls` 序列？有没有反复同 query 空转？  
3. **上下文病了吗？** 同 turn 内 system 是否变化？是否出现同 role 连发 / 合成 user？  
4. **预算够吗？** `api_calls` vs `budget_max`；grace 是否浪费在又一次 tool_call？

Demo 的 `failure_run.json` 故意踩「选错工具 + role 破环 + budget 空转」三点，见 [`03_eval_harness.md`](./03_eval_harness.md)。

---

## 5. 外接 Observability（了解即可）

完整 Hermes 可挂 LangFuse 等插件（**opt-in**）。本模块教学 **不依赖** 第三方：冻结 Trace + session 日志切片就够讲清 Observability 三板斧。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    CORE["Hermes 内建<br/>log + session_tag"] --> DEMO["教学：冻结 Trace<br/>足够讲 RCA"]
    CORE -.->|可选| EXT["LangFuse 等插件<br/>opt-in 遥测"]

    style CORE fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style DEMO fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style EXT fill:#CFD8DC,stroke:#37474F,stroke-width:2px,color:#111111
```

下一步：[`03_eval_harness.md`](./03_eval_harness.md)（用规则对冻结轨迹打分，失败写 RCA）。
