# Session Title Prompt

> 源文件：`agent/title_generator.py`
> 共提取 **2** 个宏 / 模板块

## 何时使用

| 项 | 说明 |
|----|------|
| **类型** | ② Auxiliary LLM — `task=title_generation`，**不进**主对话缓存前缀 |
| **时机** | 新会话有了首轮 user/assistant 交换后，后台生成 3–7 词标题（列表/gateway 展示用） |
| **变体** | 默认跟用户语言；配置钉死语言时用 `_TITLE_PROMPT_PINNED_LANGUAGE` |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"15px"},"themeCSS":".edgeLabel,.edgeLabel p{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart LR
    U["首轮对话"] --> TG["title_generator"]
    TG --> AUX["侧路 LLM<br/>_TITLE_PROMPT"]
    AUX --> T["短标题"]
    T --> UI["会话列表 / 网关"]
    U --> MAIN["主 Agent 继续<br/>互不干扰"]

    style AUX fill:#FFD54F,stroke:#F57F17,stroke-width:2px,color:#111111
    style MAIN fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style T fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

## 索引

- [`_TITLE_PROMPT`](#_title_prompt) — L22
- [`_TITLE_PROMPT_PINNED_LANGUAGE`](#_title_prompt_pinned_language) — L29

---

## `_TITLE_PROMPT`

- 行号：`title_generator.py:22`

```text
Generate a short, descriptive title (3-7 words) for a conversation that starts with the following exchange. The title should capture the main topic or intent. Write the title in the same language the user is writing in. Return ONLY the title text, nothing else. No quotes, no punctuation at the end, no prefixes.
```

---

## `_TITLE_PROMPT_PINNED_LANGUAGE`

- 行号：`title_generator.py:29`

```text
Generate a short, descriptive title (3-7 words) for a conversation that starts with the following exchange. The title should capture the main topic or intent. Write the title in {language}. Return ONLY the title text, nothing else. No quotes, no punctuation at the end, no prefixes.
```

---
