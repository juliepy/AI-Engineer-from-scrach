# System Prompt 组装（system_prompt.py）

> 源文件：`agent/system_prompt.py`
> 共提取 **1** 个宏 / 模板块

## 何时使用

| 项 | 说明 |
|----|------|
| **类型** | ① Cached System — **编排层**（stable / context / volatile） |
| **时机** | 会话启动组 system；本文件里的 `_TUI_EMBEDDED_PANE_CLARIFIER` 仅在 **TUI 嵌入面板** 场景追加 |
| **和 01 的关系** | 01 是文案宏库；02 决定宏怎么分层、何时塞进哪一段 |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"15px"},"themeCSS":".edgeLabel,.edgeLabel p{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart TB
    START["build_system_prompt_parts()"] --> ST["stable<br/>identity + guidance 宏"]
    START --> CT["context<br/>仓库规则 / 平台"]
    START --> VO["volatile<br/>memory 快照等"]
    ST --> OUT["完整 system"]
    CT --> OUT
    VO --> OUT
    TUI{"TUI 嵌入面板?"} -->|是| CL["+_TUI_EMBEDDED_PANE_CLARIFIER"]
    CL --> OUT
    TUI -->|否| OUT

    style START fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style CL fill:#FFD54F,stroke:#F57F17,stroke-width:2px,color:#111111
    style OUT fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

## 索引

- [`_TUI_EMBEDDED_PANE_CLARIFIER`](#_tui_embedded_pane_clarifier) — L115

---

## `_TUI_EMBEDDED_PANE_CLARIFIER`

- 行号：`system_prompt.py:115`

```text
 You're in its embedded terminal pane, beside the GUI chat — the user can select your output (Option-drag on macOS, Shift-drag elsewhere) and press Cmd/Ctrl+L to send it to the chat composer.
```

---
