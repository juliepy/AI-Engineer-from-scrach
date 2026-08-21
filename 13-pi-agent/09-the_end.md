# Pi 最终复习

四块拼成一套系统：**LOOP** 是循环本身，**Runtime & memory** 是记什么、发给模型什么，**Extension** 在循环外加能力，**HITL** 是人怎么插进去（steer / follow-up、挡工具），不单开一节。

入口进 Pi Interactive（slash / compact / 落盘），循环在 Pi Core（LLM ↔ tool）。compact **不进** `runLoop`。落盘发生在 `message_end`，不是等整轮结束。


---

## 目录

- [系统全景](#系统全景)
- [Runtime 分层](#runtime-分层)
- [一、LOOP](#一loop)
- [二、Runtime & memory](#二runtime--memory)
  - [两份记忆](#两份记忆)
  - [事件](#事件)
  - [Session 树](#session-树)
  - [Compaction](#compaction)
  - [System prompt](#system-prompt)
- [三、Extension](#三extension)

---

## 系统全景

黄是入口，只做 I/O。窄腰上下两块：上面 **Pi Interactive**（`coding-agent`）做 slash、compact、兜底；下面 **Pi Core**（`agent`）做队列和 `runLoop`。绿是 JSONL 树；蓝是开箱工具和扩展 / skill。

`registerCommand` 停在 Interactive。`registerTool` 写进 Core 每轮复印的工具表。

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear", "useMaxWidth": false}, "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF3B0", "primaryTextColor": "#1a1a1a", "primaryBorderColor": "#E6B800", "lineColor": "#90CAF9", "clusterBkg": "transparent", "clusterBorder": "#78909C", "titleColor": "#ECEFF1", "edgeLabelBackground": "#BBDEFB"}}}%%
flowchart TB
    subgraph Entry["Entry 接入层"]
        TUI["TUI / CLI"]
        RPC["RPC"]
        PRT["print  pi -p"]
        SDK["SDK"]
    end

    subgraph Waist["窄腰 · Agent.prompt"]
        direction TB
        subgraph piInteractive["Pi Interactive"]
            SES["AgentSession<br/>slash · compact · 兜底"]
        end
        subgraph piCore["Pi Core"]
            AG["Agent<br/>steer / followUp 队列"]
            LOOP["runLoop<br/>LLM ↔ tool · emit"]
            AG --> LOOP
        end
        SES --> AG
    end

    subgraph Persist["Persistence"]
        JSONL["JSONL 会话树"]
        CMP["compaction 行"]
    end

    subgraph Edge["Capability Edges"]
        TOOLS["read bash edit write"]
        EXT["Extensions"]
        SK["Skills"]
        TPL["Prompt templates"]
    end

    TUI & RPC & PRT & SDK --> SES
    SES --> JSONL
    SES --> CMP
    LOOP --> TOOLS
    EXT -.-> TOOLS
    EXT -.-> SES

    style TUI fill:#FFF59D,stroke:#F9A825,color:#212121
    style RPC fill:#FFF59D,stroke:#F9A825,color:#212121
    style PRT fill:#FFF59D,stroke:#F9A825,color:#212121
    style SDK fill:#FFF59D,stroke:#F9A825,color:#212121
    style SES fill:#FFCC80,stroke:#EF6C00,color:#212121
    style AG fill:#EF9A9A,stroke:#C62828,color:#212121
    style LOOP fill:#EF9A9A,stroke:#C62828,color:#212121
    style JSONL fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style CMP fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style TOOLS fill:#90CAF9,stroke:#1565C0,color:#212121
    style EXT fill:#90CAF9,stroke:#1565C0,color:#212121
    style SK fill:#90CAF9,stroke:#1565C0,color:#212121
    style TPL fill:#90CAF9,stroke:#1565C0,color:#212121
```

---

## Runtime 分层

源码主链：`cli.ts` → `AgentSession.prompt` → `Agent.prompt` → `runLoop`。

一条用户消息 = **1 次进循环前** + **N 次 LLM/Tool** + **1 次兜底**。compact 在 ① 和 ③，不进 ②。落盘在循环中的 `message_end`，不是 Finalize。兜底再 `continue()` 就是新的一次 `runLoop`。

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear", "useMaxWidth": false}, "themeVariables": {"fontSize": "14px", "primaryColor": "#FFCDD2", "primaryTextColor": "#212121", "lineColor": "#90CAF9", "clusterBkg": "transparent", "clusterBorder": "#78909C", "titleColor": "#ECEFF1"}}}%%
flowchart TB
    subgraph row[" "]
        direction LR
        subgraph Entry["入口壳"]
            direction TB
            E1["TUI / RPC / print / SDK"]
        end

        subgraph Runtime["Agent Runtime"]
            direction TB
            SES["AgentSession.prompt"]
            TC["① 进循环前<br/>slash / skill / compact"]
            CL["② runLoop<br/>while LLM ↔ Tools"]
            TF["③ 兜底<br/>retry / compact / 队列"]
            SES --> TC --> CL --> TF
        end

        subgraph Support["支撑"]
            direction TB
            SP["system-prompt 栈"]
            EXR["extensions runner"]
            CMP["compaction 循环外"]
            MR["model-runtime streamFn"]
            SP --> EXR --> CMP --> MR
        end

        subgraph Out["出口"]
            direction TB
            DB["JSONL append"]
            UI["handleEvent 画"]
            DB --> UI
        end
    end

    Entry --> Runtime
    Runtime -.-> Support
    Runtime --> Out

    style E1 fill:#FFF59D,stroke:#F9A825,color:#212121
    style SES fill:#EF9A9A,stroke:#C62828,color:#212121
    style TC fill:#FFF59D,stroke:#F9A825,color:#212121
    style CL fill:#FFCC80,stroke:#EF6C00,color:#212121
    style TF fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style SP fill:#CE93D8,stroke:#8E24AA,color:#212121
    style EXR fill:#CE93D8,stroke:#8E24AA,color:#212121
    style CMP fill:#CE93D8,stroke:#8E24AA,color:#212121
    style MR fill:#CE93D8,stroke:#8E24AA,color:#212121
    style DB fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style UI fill:#A5D6A7,stroke:#2E7D32,color:#212121
```

---

## 一、LOOP

一次 `prompt` 不是调一次 LLM。内层消化 tool 和 steering（中途纠偏，当前这批工具不跳过）；外层消化 follow-up（没有 tool、也没有 steering、本要停了才加一句）。有 tool 时内层会再调 LLM，不先看 follow-up。续跑不连回起点：那是同一轮再调 LLM，或兜底开的**新**一次 `runLoop`。人插进去就是这两条队列，挡工具走 `beforeToolCall`（扩展 `on("tool_call")`）。

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear", "useMaxWidth": false}, "themeVariables": {"fontSize": "14px", "primaryColor": "#FFCDD2", "primaryTextColor": "#212121", "lineColor": "#90CAF9", "edgeLabelBackground": "#BBDEFB"}}}%%
flowchart TD
    U["User Message"] --> P["① Interactive<br/>slash / skill / compact"]
    P --> SL{"扩展命令?"}
    SL -->|是| CMD["handler 结束"]
    SL -->|否| BUSY{"正在跑?"}
    BUSY -->|是| Q["steer / followUp 入队"]
    BUSY -->|否| W["② runLoop"]

    W --> LLM["stream LLM"]
    LLM --> ERR{"error / abort?"}
    ERR -->|是| AE1["立刻 agent_end"]
    ERR -->|否| TC{"有 tool?"}

    TC -->|有| BTC{"beforeToolCall 挡?"}
    BTC -->|是| FAIL["error result"]
    BTC -->|否| EX["executeToolCalls"]
    FAIL --> NEXT1["续跑 LLM"]
    EX --> NEXT2["续跑 LLM"]

    TC -->|无| ST{"steering?"}
    ST -->|有| NEXT3["续跑 LLM"]
    ST -->|无| FU{"follow-up?"}
    FU -->|有| NEXT4["续跑 LLM"]
    FU -->|无| AE2["agent_end"]

    AE1 --> F1["③ 兜底"]
    AE2 --> F2["③ 兜底"]
    F1 --> CONT1{"retry / compact / 新入队?"}
    F2 --> CONT2{"retry / compact / 新入队?"}
    CONT1 -->|是| C1["continue 新 runLoop"]
    CONT1 -->|否| DONE1["settled"]
    CONT2 -->|是| C2["continue 新 runLoop"]
    CONT2 -->|否| DONE2["settled"]

    style U fill:#90CAF9,stroke:#1565C0,color:#212121
    style P fill:#FFF59D,stroke:#F9A825,color:#212121
    style W fill:#FFCC80,stroke:#EF6C00,color:#212121
    style LLM fill:#FFAB91,stroke:#D84315,color:#212121
    style EX fill:#A5D6A7,stroke:#43A047,color:#212121
    style F1 fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style F2 fill:#A5D6A7,stroke:#2E7D32,color:#212121
    style DONE1 fill:#E0E0E0,stroke:#616161,color:#212121
    style DONE2 fill:#E0E0E0,stroke:#616161,color:#212121
    style SL fill:#BBDEFB,stroke:#1565C0,color:#212121
    style BUSY fill:#BBDEFB,stroke:#1565C0,color:#212121
    style ERR fill:#BBDEFB,stroke:#1565C0,color:#212121
    style TC fill:#BBDEFB,stroke:#1565C0,color:#212121
    style BTC fill:#BBDEFB,stroke:#1565C0,color:#212121
    style ST fill:#BBDEFB,stroke:#1565C0,color:#212121
    style FU fill:#BBDEFB,stroke:#1565C0,color:#212121
    style CONT1 fill:#BBDEFB,stroke:#1565C0,color:#212121
    style CONT2 fill:#BBDEFB,stroke:#1565C0,color:#212121
```

---

## 二、Runtime & memory

磁盘上是整棵树，发给模型的是当前这条 path。循环不画 UI、不写盘，只 `await emit`。UI 被踢出 await，不挡循环。

### 两份记忆

旁支、旧原文、custom 条目都还在文件里。`runLoop` 只吃 `AgentContext`：循环外叠好的 system prompt、按 compaction 裁过的当前 path、tools schema（不写进 prompt 正文）。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 32, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,.cluster-label,span{font-size:22px!important}"}}%%
flowchart LR
    DISK["磁盘：整棵 JSONL"] --> PATH["当前 leaf 回溯"]
    PATH --> CUT["按摘要裁"]
    CUT --> CTX["AgentContext"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef step fill:#A5F3FC,stroke:#67E8F9,color:#155E75,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px

    class DISK start
    class PATH step
    class CUT prod
    class CTX ok
```

### 事件

`await emit` 等的是 Interactive 做完（扩展钩子 + `message_end` 落盘），不是等 TUI。TUI 订 `session.subscribe`，`_emit` 不等待。文件只 append。`message_update` 只改 `streamingMessage`，不写盘。

`Agent.waitForIdle` 等的是 `agent_end` 的 listener。`AgentSession.waitForIdle` 等的是兜底之后的 `agent_settled`。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 32, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,.cluster-label,span{font-size:22px!important}"}}%%
flowchart RL
    subgraph uiLayer["UI"]
        direction TB
        HEV["handleEvent<br/>订 session.subscribe"]
        DRAW["requestRender"]
        HEV --> DRAW
    end

    subgraph interactiveLayer["Interactive"]
        direction TB
        HA["_handleAgentEvent<br/>订 agent.subscribe"]
        EXT["① await pi.on"]
        UIEMIT["② _emit 不等待"]
        DISK["③ message_end 落盘"]
        HA --> EXT
        EXT --> UIEMIT
        UIEMIT --> DISK
    end

    subgraph coreLayer["Pi Core"]
        direction TB
        LOOP["runLoop emit"]
        ST["processEvents<br/>先改 state"]
        LIS["再 await listeners"]
        LOOP --> ST
        ST --> LIS
    end

    LIS --> HA
    UIEMIT --> HEV

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef step fill:#A5F3FC,stroke:#67E8F9,color:#155E75,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A,font-size:22px

    class LOOP start
    class ST,LIS,HA,EXT,UIEMIT step
    class HEV prod
    class DISK,DRAW ok
    class uiLayer,interactiveLayer,coreLayer wrap
```

### Session 树

按 cwd 落到 `~/.pi/agent/sessions/<safe-cwd>/`。第一行是 `type: session` 的 header，之后每行一个 entry：`id` / `parentId`。当前对话位置是 `leafId`。绿是当前 path，紫的旁支仍在同一个文件里。

`/tree` 是同文件切枝（`navigateTree`）；`/fork` `/clone` 开新 JSONL。streaming 时 `navigateTree` 会抛错，界面要先 abort 再切。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 32, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,span{font-size:22px!important}"}}%%
flowchart TB
    R["根"] --> A["leaf A"]
    R --> B["leaf B 当前"]
    A --> A2["A 的后续"]
    B --> B2["B 的后续"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px

    class R start
    class B,B2 ok
    class A,A2 prod
```

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 28, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,span{font-size:22px!important}"}}%%
flowchart TB
    NOW["当前 leaf"] --> Q{"同文件切枝?"}
    Q -->|是| T["/tree navigateTree"]
    T --> B["branch，旧枝仍在"]
    Q -->|否| F["/fork /clone"]
    F --> C["新 JSONL"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef dec fill:#FEF08A,stroke:#FDE047,color:#713F12,font-size:22px
    classDef step fill:#A5F3FC,stroke:#67E8F9,color:#155E75,font-size:22px
    classDef bad fill:#FBCFE8,stroke:#F9A8D4,color:#831843,font-size:22px

    class NOW start
    class Q dec
    class T,B step
    class F,C bad
```

### Compaction

两处检查：发消息前、一轮结束后。模型正在说话时不压。已经撑爆可以丢掉失败回复再跑；快满了只压不重跑。磁盘旧行不改，末尾多一条 `compaction`。下次发给模型时换成 `<summary>`。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 28, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,span{font-size:22px!important}"}}%%
flowchart TB
    IN["_checkCompaction"] --> SKIP{"skip gate?"}
    SKIP -->|是| N1["return"]
    SKIP -->|否| OV{"overflow / length?"}
    OV -->|是| SR{"willRetry?"}
    SR -->|是| Y1["_runAutoCompaction<br/>overflow retry"]
    SR -->|否| Y2["_runAutoCompaction<br/>overflow"]
    OV -->|否| U{"usage valid?"}
    U -->|否| N2["return"]
    U -->|是| TH{"over reserve?"}
    TH -->|是| Y3["_runAutoCompaction<br/>threshold"]
    TH -->|否| N3["return"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef dec fill:#FEF08A,stroke:#FDE047,color:#713F12,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef bad fill:#FBCFE8,stroke:#F9A8D4,color:#831843,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px

    class IN start
    class SKIP,OV,SR,U,TH dec
    class Y1 bad
    class Y2,Y3 prod
    class N1,N2,N3 ok
```

| 门 | 源码条件 | 含义 |
|----|----------|------|
| skip gate | `enabled==false` / 一轮结束后遇到 `aborted` / assistant 早于最近 compaction | 这一轮根本不该压 |
| overflow / length | **同模型**且 `isContextOverflow` 或 `isRecoverableLength` | 这一句已经撑爆或被截断。换过模型则跳过这门，仍可走 threshold |
| willRetry | overflow 分支里 `stopReason != stop` | 摘掉失败 assistant，压完 `continue`；`stop` 则只压不重跑 |
| usage valid | `calculateContextTokens` 或 `estimateContextTokens` 能拿到数 | 没有有效 usage 就不走 threshold |
| over reserve | `tokens > contextWindow - reserveTokens` | 还没爆，但留给下一句的空位不够 |

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 28, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,span{font-size:22px!important}"}}%%
flowchart TB
    PATH["buildSessionPath"] --> HAS{"compaction?"}
    HAS -->|无| ALL["整段原文"]
    HAS -->|有| KEEP["摘要 + 切点之后"]
    ALL --> LLM1["AgentContext.messages"]
    KEEP --> LLM2["摘要包进 summary 再送"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef dec fill:#FEF08A,stroke:#FDE047,color:#713F12,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px

    class PATH start
    class HAS dec
    class ALL,KEEP prod
    class LLM1,LLM2 ok
```

### System prompt

tools schema 走 `context.tools`。system prompt 是栈，不是单文件覆盖。项目 `.pi/SYSTEM.md` 替换全局那份；`AGENTS.md` / `CLAUDE.md` 可以从 `~/.pi/agent/` 叠到 cwd。skill 列表要有 `read` 才挂，只写 name / description / location，模型用 `read` 去拉正文；用户打 `/skill:name` 会把 SKILL.md **全文**塞进这一句。自定义 `/template` 同样在 Interactive 展开成全文。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 28, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,span{font-size:22px!important}"}}%%
flowchart TB
    L1["default / SYSTEM.md"] --> L2["APPEND_SYSTEM.md"]
    L2 --> L3["AGENTS.md / CLAUDE.md"]
    L3 --> L4["skills listing<br/>有 read 才挂"]
    L4 --> L5["cwd"]

    classDef a fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px
    classDef b fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef c fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef d fill:#FEF08A,stroke:#FDE047,color:#713F12,font-size:22px
    classDef e fill:#FBCFE8,stroke:#F9A8D4,color:#831843,font-size:22px

    class L1 a
    class L2 b
    class L3 c
    class L4 d
    class L5 e
```

---

## 三、Extension

循环只认眼前这份工具表。缺的能力写 TS 扩展，不改 Core。默认启用四个工具（read / bash / edit / write），另有 grep / find / ls 定义但不默认打开。没有 MCP、子智能体、权限弹窗。

`registerTool` 进工具表；`registerCommand` 就地执行、不进 `Agent.prompt`；`on("tool_call")` 接到 Core 的 `beforeToolCall`，可以挡住一次工具。`pi -ne` 跳过目录和 package，仍加载 `-e`。`pi install` 写的是 `settings.packages`，不会出现在 `extensions/` 里。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 28, "nodeSpacing": 24, "padding": 12, "useMaxWidth": false, "htmlLabels": true}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,span{font-size:22px!important}"}}%%
flowchart TB
    RELOAD["resourceLoader.reload"] --> NE{"-ne?"}
    NE -->|是| E1["只加载 -e"]
    NE -->|否| SRC["packages + 目录 + settings.extensions + -e"]
    E1 --> J1["jiti 加载"]
    SRC --> J2["jiti 加载"]
    J1 --> W1{"注册了什么?"}
    J2 --> W2{"注册了什么?"}
    W1 -->|工具| T1["registerTool"]
    W1 -->|斜杠命令| C1["registerCommand"]
    W1 -->|钩子| H1["on tool_call"]
    W1 -->|provider| P1["registerProvider"]
    W2 -->|工具| T2["registerTool"]
    W2 -->|斜杠命令| C2["registerCommand"]
    W2 -->|钩子| H2["on tool_call"]
    W2 -->|provider| P2["registerProvider"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef step fill:#A5F3FC,stroke:#67E8F9,color:#155E75,font-size:22px
    classDef dec fill:#FEF08A,stroke:#FDE047,color:#713F12,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px
    classDef bad fill:#FBCFE8,stroke:#F9A8D4,color:#831843,font-size:22px

    class RELOAD start
    class E1,SRC,J1,J2 step
    class NE,W1,W2 dec
    class T1,T2 prod
    class C1,C2 ok
    class H1,H2,P1,P2 bad
```

---
