---
name: mermaid-better
description: >-
  Draws compact, readable mermaid flowcharts with dark theme, straight edges,
  a top-down decision spine, and a fixed color palette. Use when creating,
  editing, or redrawing mermaid diagrams in markdown notes, especially
  流程图 / flowchart / mermaid.
---

# Mermaid Better

画或改 mermaid 图时遵循本 skill。细则、模板、配色见 [mermaid_better.md](mermaid_better.md)。

## 硬规则

1. **直线**：`flowchart.curve` 必须是 `linear`。禁止默认贝塞尔弧，禁止 `stepAfter` / `step`。
2. **判断链用 TB**：否/继续往下，是/结束往右。LR 只给无回边的短流水线。
3. **并排分层用 RL**：左 UI / 中产品 / 右 Core 时，`flowchart RL` + 列内 `direction TB`。事件从右往左。`LR` 会把 Core 排到左边。
4. **不要绕圈**：禁止连回起点的回边。循环写在节点上，或落到「续跑」终点。
5. **不要多线汇合**：每个「是」接到自己的结果框，哪怕文案相同。订/setup 不要再连进同一处理节点。
6. **标签要短**：菱形 ≤ 约 12 字，以 `?` 结尾；边上只写 `是` / `否` / `有` / `无`。分区标题一两个词（`UI`，不要 `UI · InteractiveMode + tui`）。
7. **字号写进 classDef**：每个 `classDef` 带 `font-size:22px`，init 里加 `themeCSS` + `useMaxWidth: false`。禁止只改 `themeVariables.fontSize`（预览把 SVG 缩到栏宽，15→16 看不出）。
8. **皮肤**：dark、黑底、固定 `classDef` 配色。subgraph id 不要和 class 同名（不要 `subgraph core` + `classDef core`）。

出图前先读 mermaid_better.md 的模板和「好 vs 坏」。
