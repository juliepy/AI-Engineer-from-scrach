# Pi Interactive


---

## 目录

- [一、独立包，三种模式](#一独立包三种模式)
- [二、CLI 怎么接到 Core](#二cli-怎么接到-core)
- [三、TUI](#三tui)
- [四、进 Core 之前拦输入](#四进-core-之前拦输入)
- [对照](#对照)

---

## 一、独立包，三种模式

Pi Core 是 agent 本身。Pi Interactive 是另一个包：CLI + TUI + slash / skill 拦截。TUI、RPC、print 都从 `Agent.prompt` 进同一套 Core。`AgentSession` 不是第四套循环。三层调用栈见 `02-agent-loop.md`。事件怎么画到 TUI / JSONL，见 `03-events.md`。

```text
function flow（三种模式）
  main.ts resolveAppMode
    stdin+stdout 都是 TTY → interactive  → InteractiveMode.run()
    --mode rpc            → RPC          → runRpcMode（stdin/stdout JSONL）
    pi -p / 管道 / 非 TTY → print        → runPrintMode，跑完退出
  SDK 可直接 createAgentSession()，不经过 CLI
```

| 层 | 文件 | 函数 |
|----|------|------|
| CLI | `packages/coding-agent/src/cli.ts` · `main.ts` | 解析参数、加载扩展、建 session、选模式 |
| Session | `packages/coding-agent/src/core/agent-session.ts` | `prompt` / `_handlePostAgentRun` |
| 组装 | `packages/coding-agent/src/core/sdk.ts` | `createAgentSession` |
| TUI | `packages/tui/src/tui.ts` | 差分渲染、Component |
| 交互模式 | `packages/coding-agent/src/modes/interactive/interactive-mode.ts` | 快捷键、`/tree`、回车 = steer |

---

## 二、CLI 怎么接到 Core

`pi` 命令先进 `cli.ts`（设 process title），再进 `main.ts`。真正初始化 Core 是创建 Agent Session 那一步。扩展在这之前装好，所以能注册 flag、改工具、订事件。

```text
function flow（main）
  parseArgs
  resolve 配置 / cwd
  加载 extensions（可用 -ne 跳过）
  createAgentSessionServices
  createAgentSessionFromServices     # 这时才初始化 Pi Core
  createAgentSessionRuntime
  resolveAppMode → interactive | rpc | print
```

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}}}%%
flowchart LR
    USER["pi"] --> CLI["cli.ts"]
    CLI --> MAIN["main.ts"]
    MAIN --> PARSE["parse args"]
    PARSE --> CFG["resolve 配置"]
    CFG --> EXT["加载 Extensions"]
    EXT --> SESS["创建 Agent Session"]
    SESS --> MODE{"运行模式"}
    MODE --> INT["interactive"]
    MODE --> RPC["RPC"]
    MODE --> PRINT["print"]

    classDef u fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef i fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef s fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef c fill:#FBCFE8,stroke:#F9A8D4,color:#831843
    classDef m fill:#BBF7D0,stroke:#86EFAC,color:#14532D

    class USER u
    class CLI,MAIN,PARSE,CFG i
    class EXT s
    class SESS c
    class MODE,INT,RPC,PRINT m
```

system prompt 在进循环前叠好，不在 `runLoop` 里拼：

```text
function flow（buildSystemPrompt）
  default | SYSTEM.md | --system-prompt
    + APPEND_SYSTEM.md
    + AGENTS.md / CLAUDE.md          # home + cwd
    + skills descriptions            # 有 read 才挂
    + cwd
  AgentContext = { systemPrompt, messages, tools }
```

`SYSTEM.md` 整段替换默认身份。`APPEND_SYSTEM.md` 追加。发现顺序：项目 `.pi/` 优先于 `~/.pi/agent/`。

---

## 三、TUI

TUI 是 Interactive 的一种壳，不是第二套 agent。自研，不用 Textual。差分渲染，所以不闪屏。每个 Component 自己 `render(width)`，可处理输入。

```text
function flow（TUI）
  InteractiveMode
    订阅 AgentEvent（与 JSONL 同一条总线）
    messages 区 / editor / footer
    回车     → streamingBehavior = "steer"
    Alt+Enter → "followUp"

  packages/tui:
    TUI 差分渲染
    Component.render(width) → 行数组
    主屏 / 备用屏
```

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "16px", "background": "#000000", "lineColor": "#CBD5E1", "edgeLabelBackground": "#111111"}}}%%
flowchart TB
    EV["AgentEvent"] --> IM["InteractiveMode"]
    IM --> MSG["messages"]
    IM --> ED["editor"]
    IM --> FT["footer"]
    ED --> KEY{"键"}
    KEY -->|"Enter"| ST["steer"]
    KEY -->|"Alt+Enter"| FU["followUp"]

    classDef a fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A
    classDef b fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8
    classDef c fill:#A5F3FC,stroke:#67E8F9,color:#155E75
    classDef d fill:#FEF08A,stroke:#FDE047,color:#713F12
    classDef e fill:#FBCFE8,stroke:#F9A8D4,color:#831843

    class EV a
    class IM b
    class MSG,ED,FT c
    class KEY d
    class ST,FU e
```

开箱这套 TUI 为 Pi 定制。扩展可以换 header / footer / widget，或另挂 GUI。RPC 客户端不经过这套 TUI，但仍用同一个 `AgentSession`。

---

## 四、进 Core 之前拦输入

用户回车后先在 Interactive 处理。命中扩展命令则不进 Core。完整分流见 `02-agent-loop.md` 第二节。这里只补 Skills 和 Prompt Templates 的差别：都是斜杠，进 Core 的东西不同。

| | Skills | Prompt Templates | Extension command |
|--|--------|------------------|-------------------|
| 触发 | `/skill:name` | `/review` 这类 | 扩展 `registerCommand` |
| 进 Core 前 | 读文件，把 **全文** 包进 `<skill name location>` | `expandPromptTemplate`，`$1` / `$@` 替换 | 就地 handler，**不进 Core** |
| system prompt | 只挂 name / description / location，并指示用 `read` | 不出现 | 不出现 |
| 模型怎么用 | 斜杠已带全文；未斜杠时按 prompt 自己 `read` | 只看到展开后的句子 | 看不到 `/命令` |

```text
function flow（skill 两条路）
  拼 system prompt:
    formatSkillsForPrompt()
    <available_skills> name + description + location
    「匹配时用 read 加载 skill 文件」

  用户打 /skill:name:
    _expandSkillCommand()
    读 SKILL.md，strip frontmatter
    发给 Core 的是 <skill> 全文，不是再等模型去 read
```

大纲常说「Interactive 只塞 name/desc/location，Core 用 read」。那是 **system prompt 列表** 的行为。当前源码里 **显式 `/skill:` 会把全文内联**。自定义 template 则永远在 Interactive 展开，Core 看不到原始 `/命令`。

换一套 CLI 可以把 `/skill:` 改成 Codex 的 `$` 或 Claude Code 的 `/command`。这件事发生在 Core 之外。

---

## 对照

大纲把「怎么接 Core」「TUI」「Skills 拦截」拆成三章。源码里它们是同一个包的三面。

| 大纲 | 源码 |
|------|------|
| Interactive 是第四套循环 | 只是 `Agent.prompt` 外面的包装 |
| TUI 框架 | `packages/tui` 自研差分渲染 |
| `/skill` 只传 location | system prompt 如此；`/skill:` 命令会内联全文 |
| custom slash 到达 Core | `expandPromptTemplate` 之后 Core 只看到普通 user 文本 |
| 三种模式三套 agent | 同一 `AgentSession`，三种壳 |

读：`main.ts` → `sdk.ts` → `agent-session.ts` `prompt` → `interactive-mode.ts` → `tui.ts` → `skills.ts` / `prompt-templates.ts` / `slash-commands.ts`。
