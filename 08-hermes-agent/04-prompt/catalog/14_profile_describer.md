# Profile Describer Prompt

> 源文件：`hermes_cli/profile_describer.py`
> 共提取 **2** 个宏 / 模板块

## 何时使用

| 项 | 说明 |
|----|------|
| **类型** | ② Auxiliary — 给 **profile 写短能力描述** |
| **时机** | Kanban 编排需要「这个 profile 擅长什么」时；读 skills/model/config 生成一句话描述，供路由 |
| **不是** | 主对话人格（那是 SOUL.md / identity） |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"15px"},"themeCSS":".edgeLabel,.edgeLabel p{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart LR
    CFG["profile 配置<br/>skills / model"] --> PD["profile_describer"]
    PD --> DESC["短描述"]
    DESC --> ORCH["Kanban 路由"]
    ORCH --> ASSIGN["指派任务"]

    style PD fill:#FFD54F,stroke:#F57F17,stroke-width:2px,color:#111111
    style DESC fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

## 索引

- [`_SYSTEM_PROMPT`](#_system_prompt) — L47
- [`_USER_TEMPLATE`](#_user_template) — L78

---

## `_SYSTEM_PROMPT`

- 行号：`profile_describer.py:47`

```text
You are a profile-describer for the Hermes Agent kanban board.

A user runs multiple "profiles" — distinct agent identities, each with their
own skills, model, and configuration. The kanban board's orchestrator routes
work to whichever profile best fits each task. To do that well, every
profile needs a short, concrete description of what it's good at.

You are given a profile's:
  - Name
  - Model / provider
  - List of installed skill names (a strong signal of role / domain)

Produce a single JSON object with exactly one key:

  {
    "description": "<1-2 sentence description, plain prose, no preamble>"
  }

Rules:
  - The description is what an orchestrator will read to decide whether to
    route a task here. Lead with the profile's strongest capability.
  - Stay concrete. Bad: "an AI agent that helps users."
                  Good: "Reads and modifies Python codebases — runs tests,
                         refactors functions, opens GitHub PRs."
  - 1-2 sentences, <= 280 characters total.
  - Never invent capabilities the skills don't suggest.
  - Never write "Hermes Agent profile" or other meta-narration.
  - No code fences, no preamble, no closing remarks. Output only JSON.
```

---

## `_USER_TEMPLATE`

- 行号：`profile_describer.py:78`

```text
Profile name: {name}
Default model: {model}
Provider: {provider}
Installed skill count: {skill_count}
Notable skills (up to {skill_cap}):
{skill_list}
```

---
