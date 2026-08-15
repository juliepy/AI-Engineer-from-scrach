# Pi 架构全解析

Pi 是一套极简、模块化的智能体系统。本文按源码结构拆解其两层设计，说明每次对话实际执行的步骤，以及如何自行扩展或复刻。

系统分为两层：

1. **Agent Core（智能体核心）**：幕后运行的智能体循环（agentic loop）。可通过 **RPC** 或 **SDK** 以编程方式调用。
2. **Pi Interactive**：独立包。在 Core 之上提供 CLI / TUI，以及技能、斜杠命令等编码智能体能力。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart LR
    subgraph entry["调用入口"]
        TUI["TUI / CLI"]
        RPC["RPC"]
        SDK["SDK 编程调用"]
    end

    subgraph interactive["Pi Interactive（独立包）"]
        CLI["CLI / TUI / 编码智能体"]
    end

    subgraph core["Pi Core"]
        LOOP["Agent Loop<br/>智能体循环"]
    end

    TUI --> CLI
    CLI --> LOOP
    RPC --> LOOP
    SDK --> LOOP

    classDef entry fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef inter fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef core fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A

    class TUI,RPC,SDK entry
    class CLI inter
    class LOOP core
    class entry,interactive,core wrap
```

源码根目录：`D:\workspace\doc\面试狂魔\人工智能面试题\pi`。下文路径相对该根目录。

文档里的 **Pi Core** = `packages/agent`（`@earendil-works/pi-agent-core`）。**Pi Interactive** = `packages/coding-agent`（`@earendil-works/pi-coding-agent`）。LLM 适配在 `packages/ai`，终端渲染在 `packages/tui`。

---

## 源码目录

```text
pi/
├── packages/
│   ├── agent/                 Core：agent loop、session 树、compaction
│   ├── ai/                    多提供商 LLM API（Anthropic / OpenAI / Gemini / ...）
│   ├── coding-agent/          Interactive：CLI、TUI 组装、tools、skills、extensions
│   ├── tui/                   自研终端 UI（差分渲染、主屏 / 备用屏）
│   ├── telemetry/             遥测契约
│   ├── protocol/              RPC 编解码
│   ├── client/ · server/      进程间协议客户端 / 服务端
│   ├── evals/                 评测
│   └── session-backends/      session 存储后端（如 sqlite-node）
└── packages/coding-agent/examples/extensions/   官方扩展示例
```

核心包展开：

```text
packages/agent/src/
├── agent-loop.ts              循环：LLM ↔ tool call
├── agent.ts                   Agent 封装
├── stream-fn.ts               流式调用边界
└── harness/
    ├── agent-harness.ts       harness 组装
    ├── system-prompt.ts       skills 段落格式化
    ├── skills.ts · prompt-templates.ts
    ├── compaction/compaction.ts
    ├── session/               parentId 树、JSONL fork
    └── tools/                 Core 侧工具实现

packages/coding-agent/src/
├── cli.ts                     `pi` 入口（设 process.title，再调 main）
├── main.ts                    解析参数、加载扩展、创建 session、选模式
├── config.ts                  ~/.pi/agent、.pi
├── core/
│   ├── agent-session.ts       Interactive 侧 session / navigateTree
│   ├── agent-session-runtime.ts  fork / clone / 换 session
│   ├── session-manager.ts     JSONL 树、branch、createBranchedSession
│   ├── system-prompt.ts       buildSystemPrompt()
│   ├── resource-loader.ts     SYSTEM.md / AGENTS.md / skills / extensions
│   ├── skills.ts · prompt-templates.ts · slash-commands.ts
│   ├── settings-manager.ts
│   ├── tools/                 read bash edit write grep find ls
│   ├── extensions/            types / loader / runner
│   └── compaction/
└── modes/
    ├── interactive/           TUI 交互（interactive-mode.ts）
    ├── rpc/                   stdin/stdout JSONL
    └── print-mode.ts          `pi -p`

packages/tui/src/
├── tui.ts · tui-main-screen.ts · tui-alt-screen.ts
├── components/                editor、markdown、scroll-view、v-stack、...
└── layout.ts

packages/ai/src/
├── providers/                 每个后端一个文件（openai.ts、anthropic.ts、...）
└── models.generated.ts        由脚本生成，不要手改
```

运行时数据（不在仓库里）：`~/.pi/agent/`（`settings.json`、`AGENTS.md`、`SYSTEM.md`、`sessions/`、`extensions/`、`skills/`、`prompts/`）。

---

## 目录

- [Pi 架构全解析](#pi-架构全解析)
- [源码目录](#源码目录)
- [一、Pi Core：智能体循环（Agent Loop）](#一pi-core智能体循环agent-loop)
  - [1. 初始化上下文（Initialize Context）](#1-初始化上下文initialize-context)
  - [2. 变换上下文（Transformation）](#2-变换上下文transformation)
  - [3. 调用大语言模型（LLM Call）](#3-调用大语言模型llm-call)
- [二、Session 与 Memory（会话与记忆）](#二session-与-memory会话与记忆)
  - [存储位置](#存储位置)
  - [为何使用 JSONL 而非 JSON](#为何使用-jsonl-而非-json)
  - [Session 是树，不是列表](#session-是树不是列表)
  - [`/tree` 导航与分叉](#tree-导航与分叉)
  - [磁盘路径与消息字段](#磁盘路径与消息字段)
- [三、Tools（工具）](#三tools工具)
- [四、Extensions（扩展）](#四extensions扩展)
- [五、Skills 与 System Prompt（技能与系统提示）](#五skills-与-system-prompt技能与系统提示)
- [六、Pi Core 与 Interactive / 其他 UI 的关系](#六pi-core-与-interactive--其他-ui-的关系)
- [七、CLI 入口（CLI Entry Point）](#七cli-入口cli-entry-point)
- [八、Terminal User Interface（终端用户界面）](#八terminal-user-interface终端用户界面)
- [九、Compaction（上下文压缩）](#九compaction上下文压缩)
  - [触发时机与 token 计量](#触发时机与-token-计量)
  - [摘要 prompt 结构](#摘要-prompt-结构)
- [十、Skills 与 Custom Prompts 的处理差异](#十skills-与-custom-prompts-的处理差异)
  - [Skills](#skills)
  - [Custom prompts](#custom-prompts)
  - [Skills 工作流](#skills-工作流)
- [十一、为什么用 TypeScript 而不是 Python](#十一为什么用-typescript-而不是-python)
- [小结](#小结)

---

## 一、Pi Core：智能体循环（Agent Loop）

Pi 的设计核心是 **agent core**，即 **agent loop（智能体循环）**：每次与 Pi 开始对话时按固定步骤执行。

打开 Pi 并发送第一条消息后，流程如下。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TD
    A["用户发送消息"] --> B["1. 初始化上下文<br/>Initialize Context"]
    B --> C["2. 变换上下文 Transformation<br/>判断是否需要 compact"]
    C --> D["3. 调用大语言模型<br/>LLM Call"]
    D --> E{"模型返回什么？"}
    E -->|"tool call"| F["执行工具"]
    F --> G["工具把结果返回给 LLM"]
    G --> D
    E -->|"纯文本回复"| H["把回复交给用户"]

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef step fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef llm fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef decision fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef tool fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D

    class A start
    class B,C step
    class D llm
    class E decision
    class F,G tool
    class H ok
```

工具调用可循环多次：复杂任务可达上百次；仅搜索网页时通常几次。模型决定不再调用工具时，直接给出文本回复。以上即每次向 Pi 发送消息时的全部过程。

步骤看起来简单，实现并不简单。Pi 的循环是 **从零手写**，没有依赖现成 agent 库。对比：

- OpenAI Agents SDK
- Vercel AI SDK
- 其他预装 agentic loop 的库（import 即可使用）

Pi 这一套完全自研。

| 路径 | 看什么 |
|------|--------|
| `packages/agent/src/agent-loop.ts` | `agentLoop()`：LLM 调用与 tool 循环 |
| `packages/agent/src/agent.ts` | Agent 封装 |
| `packages/agent/src/harness/agent-harness.ts` | Core harness 组装 |
| `packages/coding-agent/src/core/agent-session.ts` | Interactive 把 prompt 送进 Core |

---

### 1. 初始化上下文（Initialize Context）

发送第一条消息后，第一步是 **初始化上下文**：按固定顺序拼接下列内容。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TB
    subgraph ctx["初始化后的上下文（自上而下拼接）"]
        SP["System Prompt<br/>系统提示（硬编码；可用 workspace 的 system.md 覆盖）"]
        AG["agents.md<br/>home + 当前工作目录"]
        SK["Skills descriptions<br/>已加载技能的描述"]
        TD["Tool descriptions<br/>工具描述"]
        MH["Message History<br/>消息历史 / compact 后的摘要"]
        CM["Current Message<br/>当前用户消息"]
    end

    SP --> AG --> SK --> TD --> MH --> CM

    classDef prompt fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef docs fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef skill fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef tool fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef hist fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef msg fill:#BBF7D0,stroke:#86EFAC,color:#14532D
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A

    class SP prompt
    class AG docs
    class SK skill
    class TD tool
    class MH hist
    class CM msg
    class ctx wrap
```

拼装顺序：

**（1）系统提示（system prompt）**

硬编码在 Pi 中。可在 workspace 创建 `system.md` 覆盖。默认加载预置系统提示：极简，仅数行指令。

**（2）追加全部 `agents.md`**

来源包括 **home** 与 **当前工作目录**。文件名是 `agents.md`，不是 `.agents.md`。文件过多会膨胀系统提示，应控制数量。

**（3）追加技能描述（skills descriptions）**

所有已加载技能的 **description** 进入上下文。

**（4）追加工具描述**

全部工具描述进入初始化上下文。

**（5）追加消息历史 + 当前消息**

- **新对话**：无消息历史。
- **进行中的对话**：包含消息历史。
- **已被 compact 的对话**：消息历史可被 **上一轮历史的摘要（summary）** 替换。

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/system-prompt.ts` | `buildSystemPrompt()`：default / SYSTEM.md / APPEND / AGENTS / skills / cwd |
| `packages/coding-agent/src/core/resource-loader.ts` | 发现 `SYSTEM.md`、`APPEND_SYSTEM.md`、`AGENTS.md` / `CLAUDE.md` |
| `packages/coding-agent/src/core/skills.ts` | `formatSkillsForPrompt()`：系统提示里只放 description |
| `packages/agent/src/harness/system-prompt.ts` | Core 侧 skills XML 块 |
| `packages/coding-agent/src/core/tools/index.ts` | 工具 schema 进入模型 tool 列表 |

---

### 2. 变换上下文（Transformation）

第二步每次都会执行：**transformation（变换）**。

系统检查刚拼好的上下文是否需要 **compact**。若需要，则执行 compact，并用结果 **替换消息历史**。

Compact 的含义：把历史中的全部消息交给 LLM **做摘要**。

| 路径 | 看什么 |
|------|--------|
| `packages/agent/src/harness/compaction/compaction.ts` | `shouldCompact()`、`compact()`、`generateSummary()` |
| `packages/coding-agent/src/core/compaction/` | Interactive 侧压缩入口 |

---

### 3. 调用大语言模型（LLM Call）

Pi 可对接三类后端：**订阅账号**、**API Key**、**自定义 / 本地模型**。调用当前配置的提供商上的模型后，模型可能返回 **tool call**（更新文件、读文件、搜索互联网等）。工具把结果返回给 LLM；LLM 可再次发起 tool call，循环直到不再需要工具，再给出文本回复。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TB
    PI["Pi 可对接订阅、API Key 与本地模型"]

    PI --> SUB
    PI --> API
    PI --> CUS

    subgraph SUB["订阅 SUBSCRIPTION"]
        S1["ChatGPT Plus / Pro"]
        S2["GitHub Copilot"]
        S3["Claude Pro / Max<br/>不支持"]
    end

    subgraph API["API Key"]
        A1["Anthropic · OpenAI · Gemini"]
        A2["Groq · Mistral · xAI"]
        A3["OpenRouter · Fireworks"]
        A4["DeepSeek · MiniMax"]
        A5["Kimi / Moonshot · GLM · 通义千问"]
    end

    subgraph CUS["自定义 CUSTOM"]
        C1["Ollama · LM Studio · vLLM"]
        C2["OpenAI 兼容代理"]
        C3["扩展自定义 Provider"]
    end

    classDef pi fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef sub fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef api fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef cus fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef nosup fill:#FED7AA,stroke:#FDBA74,color:#9A3412
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A

    class PI pi
    class S1,S2 sub
    class S3 nosup
    class A1,A2,A3,A4,A5 api
    class C1,C2,C3 cus
    class SUB,API,CUS wrap
```

三类接入：

| 类型 | 说明 | 代表 |
|------|------|------|
| **订阅** | 用现有会员账号，不必另开 API | ChatGPT Plus/Pro、GitHub Copilot。Claude Pro/Max **不支持** |
| **API Key** | 官方或聚合网关的密钥 | Anthropic、OpenAI、Gemini、Groq、Mistral、xAI、OpenRouter、Fireworks；国产 **DeepSeek、MiniMax、Kimi（Moonshot）、智谱 GLM、通义千问** |
| **自定义** | 本地推理或自建兼容端点 | Ollama、LM Studio、vLLM、OpenAI 兼容代理；也可通过扩展注册自定义 Provider |

- 复杂任务：可达 **上百次** tool call。
- 仅搜索网页：通常几次。

| 路径 | 看什么 |
|------|--------|
| `packages/ai/src/providers/` | 各提供商适配（`openai.ts`、`anthropic.ts`、`google.ts`、`github-copilot.ts`、`deepseek.ts`、`ollama` 走 OpenAI 兼容） |
| `packages/agent/src/stream-fn.ts` | 循环与 LLM 流的边界 |
| `packages/coding-agent/src/core/model-registry.ts` | Interactive 侧模型注册 |
| `packages/coding-agent/examples/extensions/custom-provider-anthropic/` | 用 extension 注册自定义 Provider |

---

## 二、Session 与 Memory（会话与记忆）

Session 的导出、导航、回退到某一步、fork（分叉）设计简单、一致。

### 存储位置

Session 位于 **home 目录** 下，路径为：

`home` → 相关目录 → `agent` → `sessions`

`sessions` 下的子目录 **一一映射到工作目录**。例如：

- 在 `dashboard` 应用中工作 → `dashboard/` 目录
- 在 `weather app` 应用中工作 → `weather-app/` 目录

每个工作目录下存放带 ID 的 session 文件，格式为 **JSONL**。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TB
    HOME["~ / home"]
    AGENT["agent"]
    SESS["sessions"]
    D1["dashboard/"]
    D2["weather-app/"]
    D3["其他工作目录"]
    S1["session-id-1.jsonl"]
    S2["session-id-2.jsonl"]
    S3["session-id-a.jsonl"]

    HOME --> AGENT --> SESS
    SESS --> D1
    SESS --> D2
    SESS --> D3
    D1 --> S1
    D1 --> S2
    D2 --> S3

    classDef root fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef mid fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef store fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef dir fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef file fill:#FBCFE8,stroke:#F9A8D4,color:#831843

    class HOME root
    class AGENT mid
    class SESS store
    class D1,D2,D3 dir
    class S1,S2,S3 file
```

### 为何使用 JSONL 而非 JSON

JSONL 不是单个 JSON 对象，而是 **每行一个 JSON 对象** 的文本文件。

新消息只需 **在文件末尾 append 一行**。每行对象包含 `role`、`message` 等字段。

Session 按 **启动时的工作目录** 归类；每条消息是独立 JSON 对象。若使用单个 JSON 数组，更新时需要改写整份文件中的某一段。JSONL 的追加成本更低。

### Session 是树，不是列表

Session **不是线性 list**，而是 **session tree（会话树）**。

在 Pi 中导航到更早的命令或 prompt，使用 **`/tree`**。每条消息除 `role`、`message` 外还有：

- `parent`：父消息 ID
- `id`：本条消息 ID

`parent` 表示该消息可能从更早的消息 **分叉（bifurcate）**。例如：一条消息的 `parent` 为 `111`，另一条的 `id` 为 `111`，则后者在前者之前。

从同一条消息再分出另一条，即 **fork 对话**。两条消息可以共享 `parent: 111`。树结构由单文件中的 `id` / `parent` 关系构成：同一父消息可引出两段独立对话。

该设计正在被更多 AI agent 采用，替代「一条接一条」的线性列表。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TD
    P["id: 111<br/>父消息"]
    A["parent: 111<br/>分叉 A：继续原对话"]
    B["parent: 111<br/>分叉 B：fork 出的新对话<br/>例如：总结此前对话"]

    P --> A
    P --> B

    classDef parent fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef branchA fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef branchB fill:#FBCFE8,stroke:#F9A8D4,color:#831843

    class P parent
    class A branchA
    class B branchB
```

JSONL 中 **所有分叉消息仍在同一文件、同一目录**。树是逻辑结构，不是物理拆文件。

### `/tree` 导航与分叉

执行 **`/tree`** 后，沿 JSONL **纵向** 浏览消息。消息类型包括 **tool call**、user message、assistant message 等。

若回到某条消息并要求 **总结对话前半部分**：系统在 JSONL 中 **新建一条消息**，将其挂到分叉点之前那条消息的 **parent / child** 关系上。其余消息仍在同一目录、同一 JSONL 中。

再次打开 `/tree` 可见分叉：一侧是 summary，一侧是原对话，可从任一侧继续。

### 磁盘路径与消息字段

路径形态：`Pi` → `Agent` → `Sessions`。其下按曾运行 Pi 的工作目录存放 session。目录名是路径的标准化形式，不是原始显示名。例如：

`Users / Alejandro / Agent Skills / Video Tool`

某一工作目录下可有多个 session 文件。每个文件是 JSONL：每行一对花括号 `{ ... }`，记录一条事件。

用编辑器打开可见：

- **每一行 = 一条消息**
- 字段包括：消息类型（可为 message）、**id**、**parent id**（建树）、**timestamp**、消息正文

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/session-manager.ts` | JSONL 树：`id` / `parentId`、`branch()`、`getTree()`、`createBranchedSession()`、`continueRecent()` |
| `packages/coding-agent/src/core/agent-session.ts` | `navigateTree()`：同文件切枝（`/tree`） |
| `packages/coding-agent/src/core/agent-session-runtime.ts` | `fork()`：新开 session 文件（`/fork`、`/clone`） |
| `packages/coding-agent/src/modes/interactive/components/tree-selector.ts` | `/tree` UI |
| `packages/agent/src/harness/session/types.ts` | Core 侧 `parentId`、`ForkOptions` |
| `packages/agent/src/harness/session/jsonl/` | Core 侧 JSONL 持久化与 `fork()` |
| `packages/coding-agent/src/config.ts` | `getAgentDir()` → `~/.pi/agent`；session 目录在其下 `sessions/` |

---

## 三、Tools（工具）

Pi 默认工具集同样极简，开箱仅 **四个**：

1. **read**
2. **bash**
3. **edit**
4. **write**

可自行增加工具：让 Pi 创建新工具，或通过安装包注册。默认只有上述四个。常见加装项是 **web search**。

另有两个额外工具：**grep** 与 **find**。二者能力可用 bash 复现，**默认禁用**，仅在 **只读模式（read-only mode）** 下启用。

只读场景通常不授予 bash。启动示例：

```text
pi --tools read,grep,find
```

参数为 **`--tools`**，后接工具列表。结果是只读 Pi（例如仅 read、grep、find）。适用于 **编程调用**（如 **RPC**）与自动化工作流：不需要写文件时，不应暴露 edit / write / bash。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart LR
    subgraph builtin["开箱四个工具"]
        R["read"]
        B["bash"]
        E["edit"]
        W["write"]
    end

    subgraph extra["额外工具（默认禁用）"]
        G["grep"]
        F["find"]
    end

    subgraph optional["常见自行加装"]
        WS["web search"]
    end

    subgraph readonly["只读模式"]
        RO["--tools read,grep,find<br/>无 bash / edit / write"]
    end

    classDef read fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef write fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef extra fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef opt fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef ro fill:#BBF7D0,stroke:#86EFAC,color:#14532D
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A

    class R read
    class B,E,W write
    class G,F extra
    class WS opt
    class RO ro
    class builtin,extra,optional,readonly wrap
```

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/tools/index.ts` | `allToolNames`、`createCodingTools()`、`createReadOnlyTools()` |
| `packages/coding-agent/src/core/tools/read.ts` | read |
| `packages/coding-agent/src/core/tools/bash.ts` | bash |
| `packages/coding-agent/src/core/tools/edit.ts` | edit |
| `packages/coding-agent/src/core/tools/write.ts` | write |
| `packages/coding-agent/src/core/tools/grep.ts` · `find.ts` · `ls.ts` | 额外工具；只读模式才默认启用 |
| `packages/agent/src/harness/tools/` | Core 侧对应实现 |
| `packages/coding-agent/src/cli/args.ts` | `--tools` |

---

## 四、Extensions（扩展）

扩展是可安装的包，用于 **修改 Pi 的行为**。默认极简：四个工具，**不内置 MCP**，**不内置 web search**。安装扩展后即可获得这些能力。

扩展能力包括：

- **Register new tools**：注册新工具
- **Subscribe to events**：订阅事件
- **Register commands**：注册命令
- **Add keyboard shortcuts**：添加键盘快捷键
- **Add CLI flags**：添加 CLI 参数
- **Update the system prompt**：更新系统提示
- **Render custom messages**：渲染自定义消息

对话工作流的 **每个环节都会触发事件**，例如 tool call、agent response、user message。扩展可订阅这些事件，在循环的 **特定时刻** 执行动作。

扩展用 **TypeScript** 编写。Pi 模块化：接入扩展即可改变行为。官方网站的 **packages** 列出可用扩展。

扩展会在本机 **加载并执行代码**。不要安装不可信的第三方来源；使用前应用 Pi 阅读该包源码并确认安全。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TB
    LOOP["Agent Loop 各阶段"]
    EV["事件：user message / tool call / agent response / ..."]
    EXT["Extension"]

    LOOP --> EV
    EV --> EXT

    EXT --> T["注册工具"]
    EXT --> C["注册命令"]
    EXT --> K["键盘快捷键"]
    EXT --> F["CLI flags"]
    EXT --> S["改系统提示"]
    EXT --> M["自定义渲染"]

    classDef loop fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef event fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef ext fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef cap fill:#FBCFE8,stroke:#F9A8D4,color:#831843

    class LOOP loop
    class EV event
    class EXT ext
    class T,C,K,F,S,M cap
```

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/extensions/types.ts` | `ExtensionAPI`：`registerTool` / `registerCommand` / `on(...)` / `ui` / `registerProvider` |
| `packages/coding-agent/src/core/extensions/loader.ts` | jiti 加载 `extensions/*.ts`，无需先编译 |
| `packages/coding-agent/src/core/extensions/runner.ts` | 事件分发 |
| `packages/coding-agent/docs/extensions.md` | 用法 |
| `packages/coding-agent/examples/extensions/` | 官方示例（tools、commands、plan-mode、subagent、...） |

---

## 五、Skills 与 System Prompt（技能与系统提示）

默认系统提示约 **20 行**，结构如下：

- 角色说明：helpful assistant，身份为 Pi
- **appended sections（追加段）**
- 自定义追加：在 **`.pi` 目录** 创建 **`append-system.md`**，追加到 “you are Pi” 段 **之后**
- Skills 列表：使用 **markup** 包裹每个技能的 name、description、用途等

技能使用 markup 的原因：后续 **TUI 会解析** 这些标签。

其后包含 **当前日期** 与 **当前工作目录**。

覆盖系统提示的两种方式：

1. 在 `.pi` 中创建 **`system.md`**
2. 启动时使用 **`--system-prompt`** 传入完整提示

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TD
    A["硬编码：You are Pi, a helpful assistant"] --> B["append-system.md<br/>.pi 目录，追加在 You are Pi 段之后"]
    B --> C["Skills 列表<br/>markup：name / description / ..."]
    C --> D["当前日期 + 当前工作目录"]

    O1["覆盖：.pi/system.md"]
    O2["覆盖：--system-prompt ..."]
    O1 -.-> A
    O2 -.-> A

    classDef base fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef append fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef skill fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef meta fill:#BBF7D0,stroke:#86EFAC,color:#14532D
    classDef override fill:#FBCFE8,stroke:#F9A8D4,color:#831843

    class A base
    class B append
    class C skill
    class D meta
    class O1,O2 override
```

以上为 Pi Core 的默认系统提示组装方式。掌握这些即可理解并复刻 Core 层。

磁盘上的文件名是 **`SYSTEM.md` / `APPEND_SYSTEM.md`**（大写），不是 `system.md`。

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/system-prompt.ts` | `buildSystemPrompt()` |
| `packages/coding-agent/src/core/resource-loader.ts` | `discoverSystemPromptFile()`、`discoverAppendSystemPromptFile()`、`loadContextFileFromDir()` |
| `packages/coding-agent/src/core/skills.ts` | `loadSkills()`、`formatSkillsForPrompt()` |
| `packages/coding-agent/src/cli/args.ts` | `--system-prompt` |

---

## 六、Pi Core 与 Interactive / 其他 UI 的关系

Pi Interactive 是 **独立包**，不在 pi-core 中。分工：

- **Pi Core**：智能体本身（循环、会话、工具、提示）
- **Pi Interactive**：编码智能体（CLI 入口、TUI、Skills / Slash 处理）

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart LR
    subgraph pkg2["pi-interactive 包"]
        INT["Coding Agent<br/>CLI 入口 + TUI + Skills/Slash 处理"]
    end

    subgraph pkg1["pi-core 包"]
        CORE["Agent / Loop / Session / Tools / Prompt"]
    end

    INT --> CORE
    OTHER["其他 GUI / 另一套 TUI"] --> CORE

    classDef inter fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef core fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef other fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A

    class INT inter
    class CORE core
    class OTHER other
    class pkg1,pkg2 wrap
```

开箱 TUI 为 Pi 定制实现。可以在 Core 之上接入自定义 GUI 或另一套 TUI。

| 路径 | 看什么 |
|------|--------|
| `packages/agent/` | Core：loop / session / compaction |
| `packages/ai/` | LLM 提供商 |
| `packages/coding-agent/` | Interactive：CLI + TUI 组装 + skills/slash |
| `packages/tui/` | 可替换的终端渲染库 |
| `packages/coding-agent/src/modes/rpc/` | 给 Python / Go / 其他 UI 用的 JSONL RPC |
| `packages/coding-agent/src/core/sdk.ts` | Node 进程内 SDK |

---

## 七、CLI 入口（CLI Entry Point）

新建 session、进入 CLI 时，逻辑分布在两个文件：

1. **`cli.ts`**
2. **`main.ts`**

**`cli.ts`**：接收 `pi` 命令，设置 process title 等，然后 **调用 `main`**。

**`main.ts`**：

- 解析参数（arguments）
- 解析配置（configuration）：自定义工作目录等
- **加载扩展**（extensions）
- **创建 agent session**：至此才初始化 Pi Core
- 按所选模式运行：
  - **interactive**
  - **RPC**
  - **print to STDIO**：命令行 `pi` 后直接跟 prompt

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TD
    CMD["pi 命令"] --> CLIENT["cli.ts<br/>接收命令、设置 process title"]
    CLIENT --> MAIN["main.ts"]
    MAIN --> P["解析 arguments"]
    P --> CFG["resolve configuration<br/>工作目录等"]
    CFG --> EXT["load extensions"]
    EXT --> SES["create agent session<br/>此时初始化 Pi Core"]
    SES --> MODE{"运行模式"}
    MODE --> I["interactive"]
    MODE --> R["RPC"]
    MODE --> S["print to STDIO"]

    classDef cmd fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef file fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef step fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef core fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef decision fill:#FED7AA,stroke:#FDBA74,color:#9A3412
    classDef modeI fill:#BBF7D0,stroke:#86EFAC,color:#14532D
    classDef modeR fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef modeS fill:#DDD6FE,stroke:#C4B5FD,color:#5B21B6

    class CMD cmd
    class CLIENT,MAIN file
    class P,CFG,EXT step
    class SES core
    class MODE decision
    class I modeI
    class R modeR
    class S modeS
```

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/cli.ts` | shebang + `process.title` + `main(argv)` |
| `packages/coding-agent/src/main.ts` | 参数、配置、扩展、`createAgentSession`、分发模式 |
| `packages/coding-agent/src/cli/args.ts` | `-c` / `-r` / `--tools` / `--mode` |
| `packages/coding-agent/src/modes/interactive/interactive-mode.ts` | interactive |
| `packages/coding-agent/src/modes/rpc/rpc-mode.ts` | RPC |
| `packages/coding-agent/src/modes/print-mode.ts` | print / STDIO |

---

## 八、Terminal User Interface（终端用户界面）

TUI 模块化布局：

- 下方：**input（输入）**
- 上方：**messages（消息）**
- 底部状态栏：会话与运行信息

特点：极简、**不闪烁（does not flicker）**。

实现要点：

1. **完全自研**，不使用 Textual 等库。
2. **Component-based（基于组件）**：每个组件负责自身 **rendering（渲染）**、**inputs（输入）**，并可 **动态更新**。
3. 可订阅 agent core 发出的事件。

| 路径 | 看什么 |
|------|--------|
| `packages/tui/src/tui.ts` | 共享 `TUI` 接口 |
| `packages/tui/src/tui-main-screen.ts` | 主屏：保留终端 scrollback |
| `packages/tui/src/tui-alt-screen.ts` | 备用屏：应用自己管滚动 |
| `packages/tui/src/components/editor.ts` | 输入框 |
| `packages/tui/src/components/markdown.ts` | 消息 Markdown |
| `packages/coding-agent/src/modes/interactive/interactive-mode.ts` | 把 Core 事件接到 TUI 组件 |
| `packages/coding-agent/src/modes/interactive/components/assistant-message.ts` | 上方消息 |
| `packages/coding-agent/src/modes/interactive/components/footer.ts` | 底部状态栏 |

---

## 九、Compaction（上下文压缩）

各 agent 的 compaction 策略不同。Pi 的策略是：不估算，只使用 LLM 响应中的用量信息。

部分实现用 **上下文总字符数 ÷ 4** 估算 token，尤其在尚未收到 LLM 响应时。Pi **不采用该估算**。它依赖响应中的 usage，并假定首条用户消息通常不会超长。

### 触发时机与 token 计量

Pi 调用 **`check compaction`**，时机有两处：

1. **When an agent ends**：一轮 turn 结束，给出回复（含 tool call 结果之后）
2. **Before the prompt**：真正发送消息之前

目的：避免回复时或启动时撑满 context window。

智能体响应后计量 token。部分提供商在响应中直接返回 **context tokens**，有则直接使用；无则按下式加总：

- **`usage.input`**：输入 token
- **`usage.output`**：生成 token
- **`cache.read`**
- **`cache.write`**

在每轮结束或用户发 prompt 之前，用上述结果判断是否 compact。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart TD
    T1["时机 1：agent ends（一轮结束）"] --> CHK["check compaction"]
    T2["时机 2：before the prompt"] --> CHK

    CHK --> HAS{"响应里有 context tokens？"}
    HAS -->|"有"| USE["直接使用提供商返回的 context tokens"]
    HAS -->|"没有"| SUM["usage.input + usage.output<br/>+ cache.read + cache.write"]

    USE --> DEC{"是否超过窗口 / 需要压缩？"}
    SUM --> DEC
    DEC -->|"是"| CMP["用 LLM 摘要替换 message history"]
    DEC -->|"否"| OK["继续"]

    classDef time fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef chk fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef decision fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef calc fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef compact fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D

    class T1,T2 time
    class CHK chk
    class HAS,DEC decision
    class USE,SUM calc
    class CMP compact
    class OK ok
```

### 摘要 prompt 结构

代码路径：

`packages/agent/src/harness/compaction/compaction.ts`

其中的 **summarization system prompt** 大意：

> You are a context summarization assistant. Your task is to read a conversation between a user and an AI assistant, ...
>
> The messages above are a conversation to summarize. Create a structured context checkpoint summary that another LLM will use to continue the work.

要求的结构：

- **Goal（目标）**
- **Constraints and preferences（约束与偏好）**
- **Progress**：what is done / what is in progress / what is blocked（已完成 / 进行中 / 被阻塞）
- **Key decisions（关键决策）**
- **Next steps（下一步）**
- **Critical context（关键上下文）**

各段保持简洁；**保留精确的文件路径、函数名和错误信息**。

更新已有摘要时（**update existing summary**），使用另一套略有差异的 prompt。

在仓库中 resume session 并执行 compact 后，用 **Ctrl-O** 展开，可见与上述结构一致的输出：goal、constraints and preferences、progress（done / in progress / blocked）、key decisions、next steps、critical context、original request、early progress 等。

| 路径 | 看什么 |
|------|--------|
| `packages/agent/src/harness/compaction/compaction.ts` | `shouldCompact()`、`compact()`、`generateSummary()`、摘要 prompt |
| `packages/agent/src/harness/compaction/utils.ts` | 会话序列化、文件操作列表 |
| `packages/coding-agent/src/core/compaction/` | Interactive 侧触发 |
| `packages/coding-agent/src/modes/interactive/components/compaction-summary-message.ts` | Ctrl-O 展开摘要 |

---

## 十、Skills 与 Custom Prompts 的处理差异

Skills 与 **custom prompts（自定义斜杠命令）** 是两套机制，处理位置相近但语义不同。

### Skills

Skills 是 **Markdown（`.md`）文件**，正文为详细指令。文件头（header）含 **name** 与 **description**；description 进入系统提示。

### Custom prompts

Custom prompts 即 **自定义 slash 命令**。输入 `/命令名` 后，在 **Pi Interactive 层**替换为已存储的完整 prompt。**该原始斜杠命令不会到达 Pi Core。**

CLI 读取 slash 命令，展开为 custom prompts 中保存的文本，再交给 Core。

### Skills 工作流

系统提示中有一节 **可用 skills 列表**。LLM 因此 **知道存在 skills**。

LLM **不知道** custom slash commands 的存在：它们到达 Core 时已是 **渲染完成的 prompt**。Skills **不会**在到达 Core 前被展开为全文。

用户发送：

```text
/skill: 自定义工作流名
```

该命令由 **interactive 层拦截**。**Agent core 看不到** `/skill:` 这一原始形式。其他 CLI / TUI 可用不同前缀（例如 Codex 的 `$`，或 Claude Code 的 slash）。

Interactive 层将其替换为带 **markup 标签** 的 skill 块，包含：

- **name**
- **description**
- **location（路径，关键字段）**

location 示例：

- `pi/agent/skills`
- `.agents/skills`

路径可在 **当前工作目录** 或 **home 目录**。上述字段进入 **发给模型的 message**，LLM 可见。

系统提示中有一条指令：**若调用了 skill，使用 read 工具读取该文件。** 模型随后调用 **read**，读取 location，取得全文后再继续。

Pi **不会**在 interactive 层把 skill 全文粘贴进消息。部分其他 agent 会立刻内联全文。Pi Interactive 只发送 **name、description、location**，由模型通过 **一次 tool call** 自行打开。该逻辑在 Core 之外，可替换实现。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "actorBkg": "#BFDBFE", "actorTextColor": "#1E3A8A", "actorBorder": "#93C5FD", "actorLineColor": "#C4B5FD", "signalColor": "#CBD5E1", "signalTextColor": "#FDE68A", "noteBkgColor": "#FEF08A", "noteTextColor": "#713F12", "noteBorderColor": "#FDE047", "sequenceNumberColor": "#1E3A8A"}}}%%
sequenceDiagram
    autonumber
    participant U as 用户
    participant I as Pi Interactive<br/>CLI / TUI
    participant C as Pi Core / LLM
    participant R as read 工具

    Note over U,C: Custom slash：Interactive 展开为完整 prompt，Core 看不到原始 /命令
    U->>I: /my-custom-prompt
    I->>C: 已渲染的完整 prompt

    Note over U,C: Skill：只注入 name / description / location，由模型自行 read
    U->>I: /skill: custom-workflow
    I->>C: markup：name + description + location<br/>指令：调用 skill 时用 read 读取
    C->>R: read(location)
    R-->>C: SKILL.md 全文
    C-->>U: 按技能继续工作
```

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/skills.ts` | 加载 `SKILL.md`；系统提示只挂 description |
| `packages/coding-agent/src/core/prompt-templates.ts` | `expandPromptTemplate()`：斜杠命令在 Interactive 展开 |
| `packages/coding-agent/src/core/slash-commands.ts` | `SlashCommandSource = "extension" \| "prompt" \| "skill"` |
| `packages/coding-agent/src/modes/interactive/interactive-mode.ts` | 拦截 `/skill:` 与自定义 `/命令` |
| `packages/coding-agent/src/modes/interactive/components/skill-invocation-message.ts` | skill 块渲染 |
| `packages/agent/src/harness/skills.ts` | Core 侧 skills 列表 |
| `packages/agent/src/harness/prompt-templates.ts` | Core 侧 template（若走 harness） |

---

## 十一、为什么用 TypeScript 而不是 Python

Pi 用 TypeScript，不是因为「TS 比 Python 更适合 AI」。Python 赢在训练、数值计算、数据管线。Pi 做的是另一类工作：**编码 harness + 终端 UI + 可热加载扩展**。

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}}}%%
flowchart LR
    subgraph py["Python 更合适"]
        P1["训练 / numpy"]
        P2["数据管线"]
        P3["LangChain 编排"]
    end

    subgraph ts["Pi 实际在做"]
        T1["同时等 LLM 流、工具、键盘、子进程"]
        T2["自研 TUI"]
        T3["Agent 写 .ts 扩展，立刻 /reload"]
    end

    classDef py fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef ts fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A

    class P1,P2,P3 py
    class T1,T2,T3 ts
    class py,ts wrap
```

**（1）扩展必须和宿主同语言**

这是最硬的约束。Pi 的卖点是：缺功能就让它自己写 extension，然后 `/reload`。

扩展是 **TypeScript 模块**，用 `jiti` 直接加载 `.ts`，不用先编译。Agent 改 `~/.pi/agent/extensions/*.ts`，宿主立刻执行同一份代码。若核心是 Python，要么再做一套插件 ABI，要么把 CPython 嵌进去——和「让 agent 改自己」相反。

**（2）产品是 TUI，不是 notebook**

作者在 Node 上自研 `pi-tui`：差分渲染、主屏 / 备用屏、流式 Markdown。TUI 与 extension 共享类型（`ctx.ui`、widget、confirm）。Python 也能做 TUI，但 Pi 把终端渲染当成一等包，和 loop、扩展 API 绑在一起。

**（3）分发和类型对得上**

- 用户：`npm i -g`；Pi Package 走 npm / git
- 模型列表生成进 `models.generated.ts`；工具 schema 用 Typebox
- 发布：Bun 打独立二进制
- 同类产品（Claude Code、OpenCode、Amp）也是 TS

**（4）需要 Python 时走 RPC，不重写核心**

`pi --mode rpc` 用 stdin/stdout JSONL。文档里有 Python 客户端示例。Python 当 **调用方**，TypeScript 当 **harness**。Node 进程内嵌入走 SDK。

| 路径 | 看什么 |
|------|--------|
| `packages/coding-agent/src/core/extensions/loader.ts` | jiti 加载 `.ts`，无需编译 |
| `packages/coding-agent/docs/extensions.md` | 「pi can create extensions」 |
| `packages/tui/src/` | 自研 TUI |
| `packages/coding-agent/src/modes/rpc/` | 给 Python / Go 用的 JSONL RPC |
| `packages/coding-agent/docs/rpc.md` | 含 Python 客户端示例 |
| `packages/ai/src/models.generated.ts` | 模型目录生成成 TS 类型（不要手改） |

---

## 小结

| 层级 | 职责 |
|------|------|
| **Pi Core** | 上下文初始化、变换 / compact、LLM 循环、工具执行、JSONL 会话树 |
| **Pi Interactive** | CLI 入口、自研 TUI、扩展加载、slash / skill 拦截与展开 |
| **语言选择** | TS 服务 harness / TUI / 热加载扩展；Python 通过 RPC 调用，不进 Core |

Core 可被 TUI、RPC、SDK 及其他 UI 复用。Interactive 负责人机界面与「命令到消息」的翻译，不把 skill 全文提前塞进 Core。
