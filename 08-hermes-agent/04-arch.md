# Hermes Agent — Architecture Map  - 最终篇

> 对照仓库：[`hermes-agent`](../../hermes-agent/) · README · [官方 Architecture](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture)  
> 更深的 Session / Turn / Memory 细讲见 [`01-arch.md`](./01-arch.md)

**一句话**：多种入口汇入同一个 `AIAgent` 窄腰；能力长在边缘（Tools / Skills / Plugins / Platforms），核心只做「拼 Context → 调模型 → 跑 Tool → 落盘」。

---

## JD

1. 下一代多模态 Agent Runtime
2. Eval、Sandbox、Memory 等核心 Infra
3. 云端 Agent 服务与端云协同能力
4. 内部 Harness：Agentify the whole company
5. 熟悉 TypeScript 与 Node.js 生态
6. 啃过 CC / Codex / Pi / OpenCode / Hermes 源码
7. 熟悉 Context Policy、Sandbox、Trace Analysis、Eval 等
8. 对 Agentic Engineering 有深入 insight
9. 做过 Agent Runtime / Sandbox / MicroVM
10. 做过 Evaluation / Benchmark / Observability
11. 有多模态 Agent / 算法相关经验

---


## 1. 仓库目录速查

```text
hermes-agent/
├── run_agent.py          # 🔴 AIAgent 核心循环
├── cli.py                # 🟡 经典交互 CLI
├── model_tools.py        # 工具编排入口
├── toolsets.py           # toolset 定义 / 平台预设
├── hermes_state.py       # 🟢 SQLite + FTS5
├── hermes_constants.py   # get_hermes_home() · profile 路径
├── batch_runner.py       # 轨迹批跑
│
├── agent/                # Prompt / Cache / Memory / Display
├── hermes_cli/           # hermes 子命令 · setup · plugins · skin
├── tools/                # 工具实现 + environments/
├── gateway/              # 消息网关 + platforms/
├── cron/                 # jobs.py · scheduler.py
├── plugins/              # memory / context_engine / model-providers / platforms / …
├── skills/               # 内置 skills（默认可用）
├── optional-skills/      # 需显式 install
├── ui-tui/ + tui_gateway/# Ink TUI
├── apps/desktop/         # Electron Desktop（独立聊天面）
├── acp_adapter/          # IDE ACP
├── web/ + website/       # Dashboard + Docs
└── tests/                # pytest（务必 scripts/run_tests.sh）
```

用户状态落盘：

| 路径 | 内容 |
|------|------|
| `~/.hermes/config.yaml` | 行为配置（非密钥） |
| `~/.hermes/.env` | **仅** API keys / tokens |
| `~/.hermes/memories/` | USER.md · MEMORY.md |
| `~/.hermes/SOUL.md` | 人格 |
| `~/.hermes/cron/jobs.json` | 定时任务 |
| Profile | `hermes -p <name>` → 独立 `HERMES_HOME` |

Windows 原生安装常见根：`%LOCALAPPDATA%\hermes`（与 WSL/`~/.hermes` 不同）。

---

## 2. 系统全景

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "15px",
    "primaryColor": "#FFF3B0",
    "primaryTextColor": "#1a1a1a",
    "primaryBorderColor": "#E6B800",
    "lineColor": "#90CAF9",
    "secondaryColor": "#C8E6C9",
    "tertiaryColor": "#BBDEFB",
    "clusterBkg": "transparent",
    "clusterBorder": "#78909C",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    subgraph Entry["🟡 Entry Points 接入层"]
        CLI["CLI<br/>cli.py"]
        TUI["TUI<br/>ui-tui + tui_gateway"]
        DESK["Desktop<br/>apps/desktop"]
        GW["Gateway<br/>gateway/run.py"]
        ACP["ACP<br/>acp_adapter/"]
        BATCH["Batch<br/>batch_runner.py"]
        API["API Server"]
    end

    subgraph Core["🔴 AIAgent 窄腰 · run_agent.py"]
        PB["Prompt Builder"]
        PR["Provider Resolution"]
        TD["Tool Dispatch"]
        CC["Compression & Caching"]
        API3["3 API Modes<br/>chat · codex · anthropic"]
        REG["Tool Registry<br/>70+ tools / ~28 toolsets"]
        PB --- PR --- TD
        CC --- API3 --- REG
    end

    subgraph Persist["🟢 Persistence"]
        DB["SessionDB<br/>SQLite + FTS5"]
        FILES["SOUL / MEMORY / USER.md"]
    end

    subgraph Edge["🔵 Capability Edges"]
        TERM["Terminal ×6"]
        BR["Browser ×5"]
        WEB["Web ×4"]
        MCP["MCP dynamic"]
        MEM["Memory Providers"]
        CRON["Cron Scheduler"]
        PLAT["25+ Platforms"]
    end

    CLI & TUI & DESK & GW & ACP & BATCH & API --> Core
    Core --> Persist
    Core --> Edge
    GW -.-> PLAT
    CRON -.-> GW

    style CLI fill:#FFF59D,stroke:#F9A825,color:#212121
    style TUI fill:#FFF59D,stroke:#F9A825,color:#212121
    style DESK fill:#FFF59D,stroke:#F9A825,color:#212121
    style GW fill:#FFF59D,stroke:#F9A825,color:#212121
    style ACP fill:#FFF59D,stroke:#F9A825,color:#212121
    style BATCH fill:#FFF59D,stroke:#F9A825,color:#212121
    style API fill:#FFF59D,stroke:#F9A825,color:#212121
    style PB fill:#EF9A9A,stroke:#C62828,color:#212121
    style PR fill:#EF9A9A,stroke:#C62828,color:#212121
    style TD fill:#EF9A9A,stroke:#C62828,color:#212121
    style CC fill:#EF9A9A,stroke:#C62828,color:#212121
    style API3 fill:#EF9A9A,stroke:#C62828,color:#212121
    style REG fill:#EF9A9A,stroke:#C62828,color:#212121
    style DB fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style FILES fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style TERM fill:#90CAF9,stroke:#1565C0,color:#212121
    style BR fill:#90CAF9,stroke:#1565C0,color:#212121
    style WEB fill:#90CAF9,stroke:#1565C0,color:#212121
    style MCP fill:#90CAF9,stroke:#1565C0,color:#212121
    style MEM fill:#90CAF9,stroke:#1565C0,color:#212121
    style CRON fill:#90CAF9,stroke:#1565C0,color:#212121
    style PLAT fill:#90CAF9,stroke:#1565C0,color:#212121
```

| 颜色层 | 职责 |
|--------|------|
| 黄 · Entry | 只做 I/O 与会话路由，不实现 Agent 逻辑 |
| 红 · Core | 唯一对话引擎；平台差异不进这里 |
| 绿 · Persist | transcript / 人格记忆落盘 |
| 蓝 · Edges | Tool 后端、渠道、Cron、可插拔记忆 |

---

## 3. 设计原则（读代码时的透镜）

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFF59D",
    "primaryTextColor": "#212121",
    "primaryBorderColor": "#F9A825",
    "lineColor": "#B0BEC5",
    "mainBkg": "#FFF59D",
    "textColor": "#ECEFF1"
  }
}}%%
mindmap
  root((Hermes Design))
    Prompt Caching 神圣
      Session 内 SP 尽量冻结
      禁止中途换 toolset
      唯一例外: Compression
    窄腰宽边缘
      Core 不加廉价 Tool
      Skill / CLI / Plugin / MCP 优先
    平台无关 Core
      CLI Gateway ACP Batch 共用 AIAgent
    可观察可打断
      Tool 回调可见
      Ctrl+C /stop 可中断
    Profile 隔离
      每 profile 独立 HERMES_HOME
```

| 原则 | 落地 |
|------|------|
| **Prompt stability** | System prompt 会话内不变；禁 mid-conversation 重建（压缩除外） |
| **Platform-agnostic core** | 差异在入口，不在 `run_agent.py` |
| **Loose coupling** | MCP / plugins / memory 用 registry + `check_fn`，非硬依赖 |
| **Footprint ladder** | 扩展优先：改现有 → CLI+Skill → 门控 Tool → Plugin → MCP → 新核心 Tool |

---

## 4. Agent Runtime（运行时详解）

> 源码主链：`run_agent.py`（forwarder）→ `agent/conversation_loop.py`（真 while）→ `agent/turn_context.py`（prologue）→ `agent/turn_finalizer.py`（收尾）  
> 细讲笔记：[`02-run-agent/`](./02-run-agent/) · 官方 [Agent Loop](https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop)

**一句话**：一条用户消息 = **1 次 Prologue** + **N 次 API/Tool 循环** + **1 次 Finalize**。Runtime 只管编排；平台 I/O 在入口，能力在 Tool 边缘。

### 4.1 Runtime 分层鸟瞰

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFCDD2",
    "primaryTextColor": "#212121",
    "lineColor": "#90CAF9",
    "clusterBkg": "transparent",
    "clusterBorder": "#78909C",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    subgraph Entry["🟡 入口壳"]
        E1["CLI / TUI / Desktop / Gateway / ACP / Cron"]
    end

    subgraph Runtime["🔴 Agent Runtime"]
        direction TB
        RA["AIAgent<br/>run_agent.py"]
        TC["① turn_context<br/>build_turn_context"]
        CL["② conversation_loop<br/>while API ↔ Tools"]
        TF["③ turn_finalizer<br/>persist + memory flush"]
        RA --> TC --> CL --> TF
    end

    subgraph Support["🟣 支撑子系统"]
        PB["prompt_builder / system_prompt"]
        PR["runtime_provider"]
        MT["model_tools + registry"]
        CMP["context_compressor"]
        AUX["auxiliary_client"]
        BUD["IterationBudget"]
    end

    subgraph Out["🟢 出口"]
        DB["SessionDB"]
        CB["callbacks · spinner · delivery"]
    end

    Entry --> Runtime
    Runtime -.-> Support
    TF --> Out

    style E1 fill:#FFF59D,stroke:#F9A825,color:#212121
    style RA fill:#EF9A9A,stroke:#C62828,color:#212121
    style TC fill:#FFF59D,stroke:#F9A825,color:#212121
    style CL fill:#FFCC80,stroke:#EF6C00,color:#212121
    style TF fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style PB fill:#CE93D8,stroke:#8E24AA,color:#212121
    style PR fill:#CE93D8,stroke:#8E24AA,color:#212121
    style MT fill:#CE93D8,stroke:#8E24AA,color:#212121
    style CMP fill:#CE93D8,stroke:#8E24AA,color:#212121
    style AUX fill:#CE93D8,stroke:#8E24AA,color:#212121
    style BUD fill:#CE93D8,stroke:#8E24AA,color:#212121
    style DB fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style CB fill:#A5D6A7,stroke:#2E7D32,color:#212121
```

| 层 | 文件 | 每用户 Turn 跑几次 |
|----|------|-------------------|
| Prologue | `turn_context.py` | **1** — 拼 messages、复用/建 SP、预压缩 |
| Loop | `conversation_loop.py` | **N** — 调模型 + 跑 tool |
| Finalize | `turn_finalizer.py` | **1** — 落库、memory/skill 回顾、返回 dict |

### 4.2 一个 Turn 的主干状态机

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFCDD2",
    "primaryTextColor": "#212121",
    "lineColor": "#90CAF9",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TD
    U["👤 User Message"] --> P["① Prologue<br/>build_turn_context"]
    P --> CX{"Codex 专用模式?"}
    CX -->|是| CDX["整 turn 交给 Codex 子进程"]
    CX -->|否| W["② while 循环"]

    W --> INT{"/stop · interrupt?"}
    INT -->|是| F
    INT -->|否| BUD["扣 IterationBudget<br/>grace 轮不扣"]
    BUD --> PRE["③ Pre-API<br/>修 role · steer · 可选再压"]
    PRE --> API["④ LLM API Call<br/>tools=schema"]
    API --> ERR{"失败?"}
    ERR -->|是| BYP["旁路: retry / compress / failover"]
    BYP --> W
    ERR -->|否| TC{"有 tool_calls?"}

    TC -->|无| TXT["⑥ 纯文本回复"]
    TXT --> VER{"需 verify / 续跑?"}
    VER -->|是| W
    VER -->|否| GRACE
    TC -->|有| EX["⑤ 执行 Tools"]
    EX --> APP["append assistant + tool msgs"]
    APP --> W

    GRACE{"⑦ 预算尽且末条是 tool?"}
    GRACE -->|是| GCALL["再调一次 API<br/>通常禁用 tools 收尾"]
    GRACE -->|否| F
    GCALL --> F
    CDX --> F
    F["⑧ Finalize<br/>DB + Memory Update"] --> DONE["✅ 返回 dict"]

    style U fill:#90CAF9,stroke:#1565C0,color:#212121
    style P fill:#FFF59D,stroke:#F9A825,color:#212121
    style W fill:#FFCC80,stroke:#EF6C00,color:#212121
    style API fill:#FFAB91,stroke:#D84315,color:#212121
    style EX fill:#A5D6A7,stroke:#43A047,color:#212121
    style F fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style DONE fill:#E0E0E0,stroke:#616161,color:#212121
    style CX fill:#BBDEFB,stroke:#1565C0,color:#212121
    style INT fill:#BBDEFB,stroke:#1565C0,color:#212121
    style ERR fill:#BBDEFB,stroke:#1565C0,color:#212121
    style TC fill:#BBDEFB,stroke:#1565C0,color:#212121
    style VER fill:#BBDEFB,stroke:#1565C0,color:#212121
    style GRACE fill:#BBDEFB,stroke:#1565C0,color:#212121
```

### 4.3 while 内：思考 → 工具 → 观察

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "15px",
    "primaryColor": "#FFCDD2",
    "primaryTextColor": "#212121",
    "lineColor": "#90CAF9",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TD
    BUILD["🧩 Prologue 已就绪<br/>SP + history + user"] --> CALL["📡 LLM API"]
    CALL --> DEC{tool_calls?}
    DEC -->|Yes| EXEC["⚙️ invoke / handle_function_call"]
    EXEC --> FEED["📥 append role=tool"]
    FEED --> CALL
    DEC -->|No| OUT["💬 Final response"]
    OUT --> SAVE["💾 Finalize"]

    style BUILD fill:#FFF59D,stroke:#F9A825,color:#212121
    style CALL fill:#FFCCBC,stroke:#E64A19,color:#212121
    style EXEC fill:#C8E6C9,stroke:#43A047,color:#212121
    style FEED fill:#C8E6C9,stroke:#43A047,color:#212121
    style OUT fill:#81D4FA,stroke:#0288D1,color:#212121
    style SAVE fill:#DCEDC8,stroke:#689F38,color:#212121
    style DEC fill:#BBDEFB,stroke:#1565C0,color:#212121
```

三个刹车（防死循环）：

| 机制 | 作用 |
|------|------|
| `max_iterations` | 硬上限（默认约 90，与 subagent 共享语义） |
| `IterationBudget` | 可 consume / refund（部分 housekeeping tool 可退回） |
| `_budget_grace_call` | 预算用尽后再给 **一次** 纯文本收尾 |
| `_interrupt_requested` | 用户 `/stop` / Ctrl+C；工具级也可取消 |

### 4.4 Tool 执行路径（Agent 级截胡 vs Registry）

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#E8F5E9",
    "primaryTextColor": "#212121",
    "lineColor": "#81C784",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart LR
    TC["assistant.tool_calls"] --> NAME{"tool name?"}
    NAME -->|todo / memory 等| AG["🔴 Agent 级截胡<br/>run_agent 内直接调"]
    NAME -->|其它| REG["🟢 registry.dispatch<br/>tools/*.py handler"]
    AG --> JSON["返回 JSON str"]
    REG --> JSON
    JSON --> MSG["append role=tool"]
    MSG --> LOOP["continue while"]

    style TC fill:#FFCC80,stroke:#EF6C00,color:#212121
    style AG fill:#EF9A9A,stroke:#C62828,color:#212121
    style REG fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style JSON fill:#FFF59D,stroke:#F9A825,color:#212121
```

Schema 在会话开始前就定好：`tools/*.py` register → `model_tools` 发现 → toolset 过滤 → 每次 API 的 `tools=`。中途换 toolset = 废 prompt cache，Runtime 禁止。

### 4.5 消息 role 时序（铁律）

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "13px",
    "actorBkg": "#BBDEFB",
    "actorBorder": "#1565C0",
    "actorTextColor": "#212121",
    "signalColor": "#90CAF9",
    "signalTextColor": "#ECEFF1",
    "noteBkgColor": "#FFF59D",
    "noteTextColor": "#212121",
    "noteBorderColor": "#F9A825"
  }
}}%%
sequenceDiagram
    autonumber
    participant S as system(cached)
    participant U as user
    participant A as assistant
    participant T as tool

    Note over S: Session 内字节稳定
    U->>A: Turn 开始
    A->>T: tool_call #1
    T-->>A: result #1
    A->>T: tool_call #2
    T-->>A: result #2
    A-->>U: 最终纯文本

    Note over S,T: 禁止两条同 role 连发<br/>禁止中途插入合成 user
```

内部统一 OpenAI 消息形：`role` / `content` / `tool_calls`；`reasoning` 存在 `assistant_msg["reasoning"]`。三种 API Mode 在进出 API 边界做格式转换，Loop 内看到的始终是这套。

### 4.6 三条 API Mode

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#BBDEFB",
    "primaryTextColor": "#212121",
    "primaryBorderColor": "#1565C0",
    "secondaryColor": "#BBDEFB",
    "tertiaryColor": "#E3F2FD",
    "lineColor": "#64B5F6",
    "mainBkg": "#BBDEFB",
    "nodeBorder": "#1565C0",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    IN["Internal messages<br/>OpenAI-style dicts"] --> MODE{"api_mode"}
    MODE -->|chat_completions| OC["openai.OpenAI<br/>Chat Completions"]
    MODE -->|codex_responses| RX["Responses / Codex 格式"]
    MODE -->|anthropic_messages| AN["anthropic adapter<br/>+ cache breakpoints"]
    OC & RX & AN --> OUT["解析回统一 messages"]

    style IN fill:#90CAF9,stroke:#1565C0,color:#212121
    style MODE fill:#BBDEFB,stroke:#1565C0,color:#212121
    style OC fill:#BBDEFB,stroke:#1565C0,color:#212121
    style RX fill:#BBDEFB,stroke:#1565C0,color:#212121
    style AN fill:#BBDEFB,stroke:#1565C0,color:#212121
    style OUT fill:#FFF59D,stroke:#F9A825,color:#212121
```

| Mode | 用途 | 解析优先级 |
|------|------|------------|
| `chat_completions` | OpenRouter / 多数兼容端 | 默认 |
| `codex_responses` | Codex / Responses API | 显式或 provider 探测 |
| `anthropic_messages` | 原生 Anthropic + cache | `anthropic` provider / `api.anthropic.com` |

解析顺序：构造参数 `api_mode` → provider 特判 → base_url 启发 → 默认 `chat_completions`。

### 4.7 Runtime 与周边职责边界

| 关注点 | Runtime 做 | Runtime 不做 |
|--------|------------|--------------|
| 会话路由 | 接收已解析的 history / session_id | Gateway Session Key / 排队 |
| Prompt | 复用缓存 SP；压缩时重建 | 每轮重读 SOUL/MEMORY 进 SP |
| Tool | 截胡 + registry 分发 | 新增核心 tool 的产品决策 |
| 预算 | iterations / budget / grace / interrupt | 平台侧消息防抖 |
| 落盘 | Finalize 写 SessionDB / flush memory | Cron 的 Home 投递策略 |

---

## 5. 三条主数据流

### 5.1 CLI / TUI / Desktop

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "actorBkg": "#BBDEFB",
    "actorBorder": "#1565C0",
    "actorTextColor": "#212121",
    "signalColor": "#4FC3F7",
    "signalTextColor": "#FFFFFF",
    "sequenceNumberColor": "#FFFFFF",
    "labelBoxBkgColor": "#37474F",
    "labelBoxBorderColor": "#4FC3F7",
    "labelTextColor": "#FFFFFF",
    "loopTextColor": "#FFFFFF",
    "noteBkgColor": "#FFF59D",
    "noteTextColor": "#212121",
    "noteBorderColor": "#F9A825"
  }
}}%%
sequenceDiagram
    autonumber
    participant U as User
    participant UI as CLI / TUI / Desktop
    participant A as AIAgent
    participant P as Provider
    participant T as Tools
    participant DB as SessionDB

    U->>UI: 输入 / 点击发送
    UI->>A: run_conversation()
    A->>A: build_system_prompt + resolve provider
    A->>P: chat/completions | messages
    loop Tool loop
        P-->>A: tool_calls
        A->>T: handle_function_call
        T-->>A: JSON result
        A->>P: 回灌 messages
    end
    P-->>A: final content
    A->>DB: persist transcript
    A-->>UI: 展示回复
```

### 5.2 Messaging Gateway

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#B2EBF2",
    "primaryTextColor": "#212121",
    "lineColor": "#4FC3F7",
    "clusterBkg": "transparent",
    "clusterBorder": "#90A4AE",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart LR
    subgraph Platforms["紫 · Platforms"]
        TG["Telegram"]
        DC["Discord"]
        SL["Slack"]
        WA["WhatsApp"]
        SIG["Signal"]
        MORE["… 20+"]
    end

    subgraph GW["青 · GatewayRunner"]
        AUTH["Authorize"]
        SK["Session Key"]
        HYG["Hygiene ~85%"]
        HIST["Load history"]
        SM["queue / interrupt / steer"]
    end

    AGENT["红 · AIAgent"]
    DELIV["绿 · Delivery"]

    TG & DC & SL & WA & SIG & MORE --> AUTH
    AUTH --> SK --> HYG --> HIST --> SM --> AGENT --> DELIV
    DELIV --> TG & DC & SL & WA & SIG & MORE

    style TG fill:#CE93D8,stroke:#8E24AA,color:#212121
    style DC fill:#CE93D8,stroke:#8E24AA,color:#212121
    style SL fill:#CE93D8,stroke:#8E24AA,color:#212121
    style WA fill:#CE93D8,stroke:#8E24AA,color:#212121
    style SIG fill:#CE93D8,stroke:#8E24AA,color:#212121
    style MORE fill:#CE93D8,stroke:#8E24AA,color:#212121
    style AUTH fill:#80CBC4,stroke:#00897B,color:#212121
    style SK fill:#80CBC4,stroke:#00897B,color:#212121
    style HYG fill:#80CBC4,stroke:#00897B,color:#212121
    style HIST fill:#80CBC4,stroke:#00897B,color:#212121
    style SM fill:#80CBC4,stroke:#00897B,color:#212121
    style AGENT fill:#EF9A9A,stroke:#C62828,color:#212121
    style DELIV fill:#A5D6A7,stroke:#2E7D32,color:#212121
```

Session Key 形态：`{platform}:{provider_session_id}:…` —— Gateway 每次只收到「最新一条」，必须靠 SQLite 还原整段历史。

### 5.3 Cron

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFE0B2",
    "primaryTextColor": "#212121",
    "lineColor": "#FFB74D",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TD
    TICK["⏱ Scheduler tick"] --> LOCK["🔒 .tick.lock"]
    LOCK --> LOAD["📖 jobs.json 到期 Job"]
    LOAD --> FRESH["🆕 Fresh AIAgent<br/>skip_memory · 无主会话历史"]
    FRESH --> SKILL["📎 注入 attached skills"]
    SKILL --> RUN["▶ 跑 Job prompt"]
    RUN --> OUT["📁 cron/output/&lt;job_id&gt;/"]
    OUT --> HOME["📬 投递到目标平台 / Home"]
    HOME --> NEXT["🗓 更新 next_run"]

    style TICK fill:#FFE0B2,stroke:#EF6C00,color:#212121
    style FRESH fill:#EF9A9A,stroke:#C62828,color:#212121
    style HOME fill:#80CBC4,stroke:#00695C,color:#212121
```

Cron 是 **Agent 任务**（不是 shell crontab）。交付与主 Gateway 会话隔离，避免破坏消息 role 交替。

---

## 6. Tool 系统与依赖链

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "15px",
    "primaryColor": "#E8F5E9",
    "primaryTextColor": "#212121",
    "lineColor": "#81C784",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    R["tools/registry.py<br/>无依赖 · 中央注册表"]
    T["tools/*.py<br/>import 时 registry.register()"]
    M["model_tools.py<br/>discover + handle_function_call"]
    A["run_agent.py · cli.py<br/>batch_runner · environments"]

    R --> T --> M --> A

    style R fill:#A5D6A7,stroke:#1B5E20,color:#212121
    style T fill:#C8E6C9,stroke:#2E7D32,color:#212121
    style M fill:#FFF59D,stroke:#F9A825,color:#212121
    style A fill:#FFAB91,stroke:#D84315,color:#212121
```

| 层 | 文件 | 作用 |
|----|------|------|
| Registry | `tools/registry.py` | schema / dispatch / availability / 错误包装 |
| Impl | `tools/*.py` | 自注册；handler 必须返回 JSON 字符串 |
| Orchestration | `model_tools.py` | 发现工具、组装 definitions、执行调用 |
| Exposure | `toolsets.py` | 只有进 toolset 的工具才会暴露给 Agent |
| Backends | `tools/environments/` | local · docker · ssh · modal · daytona · singularity |

**Footprint 提醒**：Terminal + File 能做的事，不要再加核心 Tool；优先 Skill / Plugin / MCP。

---

## 7. Context 体系（组装 · 缓存 · 压缩）

> 源码：`agent/system_prompt.py` · `agent/prompt_builder.py` · `agent/context_compressor.py` · `agent/turn_context.py`  
> 细讲：[`01-arch.md`](./01-arch.md) §3–4 · [`04-prompt/`](./04-prompt/) · 官方 [Prompt Assembly](https://hermes-agent.nousresearch.com/docs/developer-guide/prompt-assembly)

**一句话**：Context = **Session 冻结的 System Prompt** + **Turn 可变的消息侧**。稳定前缀保 cache；会变的东西放 messages / tool result / ephemeral，绝不每轮重写 SP。

### 7.1 Session vs Turn（两层时间尺度）

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFF8E1",
    "primaryTextColor": "#212121",
    "lineColor": "#B0BEC5",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    Boot["🟡 Session 启动<br/>读盘 → 组装 SP → Frozen Snapshot"]
    T1["🔵 Turn 1<br/>复用 SP + 拼历史/本轮 → Loop"]
    T2["🔵 Turn 2<br/>SP 仍是启动快照"]
    Tn["🔵 Turn N<br/>可 Compression 改消息历史"]
    EndS["🟢 新 Session<br/>才重读盘刷新 SP"]

    Boot --> T1 --> T2 --> Tn --> EndS

    style Boot fill:#FFF59D,stroke:#F9A825,color:#212121
    style T1 fill:#81D4FA,stroke:#0277BD,color:#212121
    style T2 fill:#81D4FA,stroke:#0277BD,color:#212121
    style Tn fill:#81D4FA,stroke:#0277BD,color:#212121
    style EndS fill:#A5D6A7,stroke:#2E7D32,color:#212121
```

| 词 | 含义 | 对 Context 的影响 |
|----|------|-------------------|
| **Session** | Desktop 一条对话 / CLI 一次聊 / Gateway 同一 `session_id` | 启动组装并 **冻结** SP |
| **Turn** | 用户 1 条消息 → 跑完 Loop → 最终回复 | 每轮 Build：复用 SP + 追加消息；可压缩 |

### 7.2 发给 LLM 的两块拼图

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFF8E1",
    "primaryTextColor": "#212121",
    "lineColor": "#90CAF9",
    "clusterBkg": "transparent",
    "clusterBorder": "#78909C",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    subgraph SP["Cached System Prompt · Session 冻结"]
        direction TB
        S["🟡 stable<br/>SOUL · Tools/Skills 指引 · 环境/平台 hint"]
        C["🟠 context<br/>system_message · Project Context 一种"]
        V["🔴 volatile<br/>MEMORY / USER 快照 · provider 块 · 时间戳"]
        S --> C --> V
    end

    subgraph MSG["Per-call Messages · Turn 可变"]
        H["历史 turns<br/>可被 Compression 摘要替换"]
        U["本轮 user"]
        E["紫 · ephemeral / plugin prefetch<br/>挂本轮 user 或 API 叠加层"]
        TR["绿 · tool results<br/>可挂子目录 AGENTS.md"]
    end

    SP --> LLM["LLM Request"]
    MSG --> LLM

    style S fill:#FFF59D,stroke:#F9A825,color:#212121
    style C fill:#FFCC80,stroke:#FB8C00,color:#212121
    style V fill:#EF9A9A,stroke:#E53935,color:#212121
    style H fill:#81D4FA,stroke:#039BE5,color:#212121
    style U fill:#81D4FA,stroke:#039BE5,color:#212121
    style E fill:#CE93D8,stroke:#8E24AA,color:#212121
    style TR fill:#C8E6C9,stroke:#43A047,color:#212121
    style LLM fill:#E0E0E0,stroke:#616161,color:#212121
```

### 7.3 System Prompt 三层注入地图

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "13px",
    "primaryColor": "#FFFDE7",
    "primaryTextColor": "#212121",
    "lineColor": "#FFD54F",
    "clusterBkg": "transparent",
    "clusterBorder": "#78909C",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    subgraph Stable["🟡 STABLE"]
        S1["SOUL.md 或 DEFAULT_IDENTITY"]
        S2["Help / Task-completion / Parallel-tool 指引"]
        S3["Memory·Skills·Kanban guidance<br/>仅当对应 tool 在 schema 里"]
        S4["Skills 索引 · Env hints · Platform hint"]
        S1 --> S2 --> S3 --> S4
    end

    subgraph Context["🟠 CONTEXT"]
        C1["调用方 system_message"]
        C2["Project Context 只选一种"]
        C1 --> C2
    end

    subgraph Volatile["🔴 VOLATILE"]
        V1["MEMORY.md 冻结快照"]
        V2["USER.md 冻结快照"]
        V3["Memory provider block"]
        V4["时间 · session · model · provider 行"]
        V1 --> V2 --> V3 --> V4
    end

    Stable --> Context --> Volatile --> JOIN["join 非空三层<br/>→ agent._cached_system_prompt"]

    style S1 fill:#FFF59D,stroke:#F9A825,color:#212121
    style C2 fill:#FFCC80,stroke:#FB8C00,color:#212121
    style V1 fill:#EF9A9A,stroke:#E53935,color:#212121
    style JOIN fill:#B0BEC5,stroke:#455A64,color:#212121
```

Project Context 优先级（每个 Session **只取一种**；`SOUL` 独立占位不抢槽）：

```text
.hermes.md / HERMES.md  →  AGENTS.md  →  CLAUDE.md  →  .cursorrules
```

**条件注入**：没加载 `memory` tool 就不塞 `MEMORY_GUIDANCE`，避免模型幻觉调用不存在的工具。

### 7.4 什么进 SP，什么绝不进 SP

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#E8EAF6",
    "primaryTextColor": "#212121",
    "lineColor": "#90CAF9",
    "clusterBkg": "transparent",
    "clusterBorder": "#78909C",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart LR
    subgraph IN["🟢 进 Cached SP"]
        A["SOUL / Skills 索引"]
        B["Project Context 一种"]
        C["MEMORY / USER 启动快照"]
        D["平台 / 环境 hint"]
    end

    subgraph OUT["🔴 不进 Cached SP"]
        E["ephemeral_system_prompt"]
        F["pre_llm_call 插件返回"]
        G["Skill slash → user message"]
        H["Compression 摘要 → history"]
        I["Honcho turn recall → user overlay"]
        J["中途 memory tool 写盘"]
    end

    IN --> SP["_cached_system_prompt"]
    OUT --> MSG["messages / API overlay"]

    style IN fill:#C8E6C9,stroke:#2E7D32,color:#212121
    style OUT fill:#FFCDD2,stroke:#C62828,color:#212121
    style SP fill:#FFF59D,stroke:#F9A825,color:#212121
    style MSG fill:#90CAF9,stroke:#1565C0,color:#212121
```

| Markdown / 块 | 进 Context 时机 | 中途写盘影响当前 SP？ |
|---------------|-----------------|----------------------|
| `SOUL.md` | Session 启动 → stable | 否（下个 Session） |
| Project Context | Session 启动 → context | 否；子目录可挂 **tool result** |
| `USER.md` / `MEMORY.md` | Session 启动 → volatile | **否** |
| Skills / Tools 描述 | Session 启动（按 schema） | 换 toolset 被禁止 |
| 消息历史 | 每 Turn | Compression 可改历史 |
| External prefetch | 常挂 Turn 侧 | 不改 SP |

Gateway 额外：每 turn 可能新建 `AIAgent`，靠 SessionDB **读回同一份 system 字符串**（`_restore_or_build_system_prompt`），否则 cache 前缀对不齐。

### 7.5 Turn 级 Build Context 流程

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#BBDEFB",
    "primaryTextColor": "#212121",
    "primaryBorderColor": "#1565C0",
    "lineColor": "#64B5F6",
    "mainBkg": "#BBDEFB",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TD
    U["用户新消息"] --> CHK{"用量 ≥ 阈值?<br/>默认 50% · 或上次 context 报错"}
    CHK -->|是| CMP["Compression<br/>旧中间段 → 结构化 Summary"]
    CHK -->|否| OK["保留完整历史"]
    CMP --> BUILD["拼本轮请求"]
    OK --> BUILD
    BUILD --> SP["复用 Session 冻结 SP"]
    BUILD --> MSG["历史 + 本轮 user<br/>+ 可选 ephemeral"]
    SP --> LLM["调用 LLM"]
    MSG --> LLM
    LLM --> DEC{"要调 Tool?"}
    DEC -->|是| TOOL["执行 Tool"]
    TOOL --> HINT{"路径触及新子目录?"}
    HINT -->|是| INJ["AGENTS.md 等追加到 tool result"]
    HINT -->|否| FEED["Result 回灌"]
    INJ --> FEED --> LLM
    DEC -->|否| RESP["最终回复"]
    RESP --> MEM["transcript 落盘<br/>可能写 USER/MEMORY<br/>≠ 刷新当前 SP"]

    style U fill:#90CAF9,stroke:#1565C0,color:#212121
    style CHK fill:#BBDEFB,stroke:#1565C0,color:#212121
    style DEC fill:#BBDEFB,stroke:#1565C0,color:#212121
    style HINT fill:#BBDEFB,stroke:#1565C0,color:#212121
    style CMP fill:#FFCC80,stroke:#EF6C00,color:#212121
    style SP fill:#FFF59D,stroke:#F9A825,color:#212121
    style INJ fill:#C8E6C9,stroke:#43A047,color:#212121
    style MEM fill:#CE93D8,stroke:#8E24AA,color:#212121
```

### 7.6 Compression（压消息，不重读说明书）

源码：`agent/context_compressor.py`。压的是 **消息列表**，不是重装 Project Context。

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFE0B2",
    "primaryTextColor": "#212121",
    "lineColor": "#FFB74D",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    IN["消息列表"] --> P1["① 廉价剪枝<br/>缩短旧 tool 输出 · 不调 LLM"]
    P1 --> P2["② 定边界<br/>head / middle / tail<br/>不拆开 tool 对"]
    P2 --> CHK{"middle 可压?"}
    CHK -->|否| NOP["无效压缩计数 · 原样返回"]
    CHK -->|是| P3["③ 辅助模型写结构化摘要<br/>可有增量更新"]
    P3 --> OK{"成功?"}
    OK -->|否| FB["中止或本地兜底摘要"]
    OK -->|是| P4["④ 组装<br/>head + Summary + tail"]
    FB --> OUT["新消息列表"]
    P4 --> OUT

    style P1 fill:#FFE0B2,stroke:#EF6C00,color:#212121
    style P2 fill:#FFCC80,stroke:#FB8C00,color:#212121
    style P3 fill:#CE93D8,stroke:#8E24AA,color:#212121
    style P4 fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style CHK fill:#BBDEFB,stroke:#1565C0,color:#212121
    style OK fill:#BBDEFB,stroke:#1565C0,color:#212121
```

| 配置（`compression:`） | 默认直觉 |
|------------------------|----------|
| `threshold: 0.50` | 用量 ≥ 窗口 50% 触发 |
| `target_ratio: 0.20` | 尾部保留预算 ≈ 触发线 × 0.2 |
| `protect_last_n: 20` | 尾部至少留 N 条 |
| Gateway Hygiene | 进 Agent 前约 **85%** 安全网 |

三段切法：`head`（开头保护）· `middle`（压成 Historical Snapshot 摘要）· `tail`（近期原文）。摘要声明「仅背景参考」，防止把旧待办当成还要继续做。

### 7.7 Context 与 Prompt Cache 的契约

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#FFECB3",
    "primaryTextColor": "#212121",
    "lineColor": "#B0BEC5",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    OK["✅ 保 Cache"] --> OK1["Session 内复用同一 SP 字节"]
    OK --> OK2["Skill slash 注入成 user message"]
    OK --> OK3["Memory 写盘等下个 Session"]
    OK --> OK4["子目录 Context 挂 tool result"]

    BAD["❌ 废 Cache"] --> BAD1["中途换 toolset / 重建 SP"]
    BAD --> BAD2["每轮重读 MEMORY 进 system"]
    BAD --> BAD3["插入合成 user 破坏 role 交替"]

    EXC["唯一例外"] --> EXC1["Context Compression<br/>改的是 messages 中段"]

    style OK fill:#C8E6C9,stroke:#2E7D32,color:#212121
    style BAD fill:#FFCDD2,stroke:#C62828,color:#212121
    style EXC fill:#FFF59D,stroke:#F9A825,color:#212121
```

速记：

```text
写了 MEMORY ≠ 当前 SP 已更新（要新 Session）
直聊可以没有 AGENTS.md（完全正常）
Gateway：拉历史在消息侧；冻 SP 与 CLI 相同
Compression：改历史，不是改 Project Context 文件
```

---

## 8. 可插拔子系统

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#E3F2FD",
    "primaryTextColor": "#212121",
    "lineColor": "#90CAF9",
    "clusterBkg": "transparent",
    "clusterBorder": "#78909C",
    "titleColor": "#ECEFF1",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    subgraph General["General Plugins"]
        PM["PluginManager<br/>hermes_cli/plugins.py"]
        HOOKS["hooks: pre/post tool · LLM · session"]
        PTOOLS["ctx.register_tool"]
        PCLI["ctx.register_cli_command"]
    end

    subgraph Specialized["Single-select Plugins"]
        MEM["Memory Provider<br/>honcho · mem0 · …"]
        CTX["Context Engine"]
        MP["Model Providers<br/>openrouter · anthropic · …"]
        IMG["Image Gen"]
    end

    subgraph Discover["Discovery Paths"]
        U["~/.hermes/plugins/"]
        P["./.hermes/plugins/"]
        E["pip entry points"]
        B["repo plugins/*"]
    end

    Discover --> PM
    Discover --> Specialized
    PM --> HOOKS & PTOOLS & PCLI

    style PM fill:#90CAF9,stroke:#1565C0,color:#212121
    style MEM fill:#CE93D8,stroke:#8E24AA,color:#212121
    style CTX fill:#CE93D8,stroke:#8E24AA,color:#212121
    style MP fill:#CE93D8,stroke:#8E24AA,color:#212121
    style IMG fill:#CE93D8,stroke:#8E24AA,color:#212121
```

| 类型 | 选择模型 | 目录 |
|------|----------|------|
| General plugin | 可多个 | `plugins/<name>/`、用户目录、pip |
| Memory provider | **同时只能一个** | `plugins/memory/` |
| Context engine | **同时只能一个** | `plugins/context_engine/` |
| Model provider | 按配置切换 | `plugins/model-providers/` |
| Platform adapter | 多开 | `gateway/platforms/` + `plugins/platforms/` |

---

## 9. Surface 对照（同一 Core，不同壳）

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "14px",
    "primaryColor": "#F3E5F5",
    "primaryTextColor": "#212121",
    "lineColor": "#CE93D8",
    "edgeLabelBackground": "#BBDEFB",
    "edgeLabelColor": "#0D47A1"
  }
}}%%
flowchart TB
    CORE["AIAgent + Tools + SessionDB"]

    CLI["经典 CLI<br/>prompt_toolkit + Rich"]
    TUI["hermes --tui<br/>Ink ↔ JSON-RPC"]
    DASH["Dashboard /chat<br/>嵌入真实 TUI PTY"]
    DESK["Desktop App<br/>自有 transcript · 不嵌 TUI"]
    MSG["Messaging Gateway<br/>Telegram …"]
    IDE["ACP · VS Code/Zed/JB"]

    CLI & TUI & MSG & IDE & DESK --> CORE
    DASH --> TUI

    style CORE fill:#EF9A9A,stroke:#C62828,color:#212121
    style CLI fill:#FFF59D,stroke:#F9A825,color:#212121
    style TUI fill:#A5D6A7,stroke:#43A047,color:#212121
    style DASH fill:#80CBC4,stroke:#00897B,color:#212121
    style DESK fill:#CE93D8,stroke:#8E24AA,color:#212121
    style MSG fill:#81D4FA,stroke:#0288D1,color:#212121
    style IDE fill:#FFCC80,stroke:#FB8C00,color:#212121
```

要点：**Dashboard 嵌 TUI；Desktop 是第三条聊天面**（经 `hermes serve` JSON-RPC），不要在 Dashboard React 里重写主对话。

---

## 10. 学习路径（建议顺序）

| # | 主题 | 本仓库笔记 / 官方 |
|---|------|-------------------|
| 1 | 仓库目录 + 全景 | `arch.md` §1–2 |
| 2 | **Agent Runtime**（图解） | `arch.md` **§4** · [`02-run-agent/`](./02-run-agent/) · [agent-loop](https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop) |
| 3 | **Context 体系**（图解） | `arch.md` **§7** · [`04-prompt/`](./04-prompt/) · [prompt-assembly](https://hermes-agent.nousresearch.com/docs/developer-guide/prompt-assembly) |
| 4 | Session / Turn / Memory 深讲 | [`01-arch.md`](./01-arch.md) · [`02-memory.md`](./02-memory.md) |
| 5 | Cron | [`06-cron/`](./06-cron/) |
| 6 | Gateway | [`08-gateway/`](./08-gateway/) |
| 7 | Memory Providers | [`07-mem-provider/`](./07-mem-provider/) |
| 8 | Tools Runtime | [tools-runtime](https://hermes-agent.nousresearch.com/docs/developer-guide/tools-runtime) |

---

## 11. 速记卡片

```text
Entry → AIAgent Runtime → (Prompt + Provider + Tools) → SessionDB / Delivery
                       ↘ Terminal/Browser/Web/MCP/Cron/Plugins

Runtime: 1 Prologue + N (API↔Tool) + 1 Finalize
         刹车 = max_iterations · IterationBudget · grace · interrupt
         Tool = agent 截胡(todo/memory) | registry.dispatch
         三 Mode 边界转换，内部统一 OpenAI messages

Context: Session 冻 SP(stable→context→volatile)
         Turn 拼 历史+user+ephemeral；子目录挂 tool result
         写 MEMORY ≠ 刷新当前 SP；压缩只改 messages 中段
Cache:   禁中途换 toolset / 重建 SP（压缩例外）

Gate:    一条消息 → Session Key → 拉历史 → 同一 Runtime
Cron:    新 Agent · 独立会话 · Home/平台投递
Edge:    能力外挂；Core 保持窄
```
