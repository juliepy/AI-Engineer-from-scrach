# Sticker Vision Prompt

> 源文件：`gateway/sticker_cache.py`
> 共提取 **1** 个宏 / 模板块

## 何时使用

| 项 | 说明 |
|----|------|
| **类型** | ② Auxiliary — `task=vision`（贴纸描述） |
| **时机** | 网关收到贴纸消息：侧路视觉模型生成 1–2 句客观描述，再参与主对话上下文（可缓存描述） |
| **不是** | 主模型 system 文案 |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"15px"},"themeCSS":".edgeLabel,.edgeLabel p{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart LR
    ST["用户发贴纸"] --> GW["gateway"]
    GW --> V["Vision + STICKER_VISION_PROMPT"]
    V --> D["1-2 句描述"]
    D --> CHAT["注入主会话理解"]

    style V fill:#FFD54F,stroke:#F57F17,stroke-width:2px,color:#111111
    style D fill:#80DEEA,stroke:#006064,stroke-width:2px,color:#111111
```

## 索引

- [`STICKER_VISION_PROMPT`](#sticker_vision_prompt) — L23

---

## `STICKER_VISION_PROMPT`

- 行号：`sticker_cache.py:23`

```text
Describe this sticker in 1-2 sentences. Focus on what it depicts -- character, action, emotion. Be concise and objective.
```

---
