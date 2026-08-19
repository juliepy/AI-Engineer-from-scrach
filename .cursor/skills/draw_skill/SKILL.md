---
name: mermaid-better
description: >-
  Draws compact, readable mermaid flowcharts with dark theme, straight edges,
  a top-down decision spine, and a fixed color palette. Use when creating,
  editing, or redrawing mermaid diagrams in markdown notes, especially
  流程图 / flowchart / mermaid.
---

# Mermaid Better

画或改 mermaid 图时遵循本 skill。细则和配色表见 [mermaid_better.md](mermaid_better.md)。

## 硬规则

1. **直线**：`flowchart.curve` 必须是 `linear`。禁止默认贝塞尔弧，禁止 `stepAfter` / `step`。
2. **判断链用 TB**：否/继续往下，是/结束往右。LR 只给无回边的短流水线。
3. **不要绕圈**：禁止连回起点的回边。循环写在节点上，或落到「续跑」终点。
4. **不要多线汇合**：每个「是」接到自己的结果框，哪怕文案相同。
5. **标签要短**：菱形 ≤ 约 12 字，以 `?` 结尾；边上只写 `是` / `否` / `有` / `无`。
6. **疏密**：`rankSpacing` 28–36，`nodeSpacing` 24，`padding` 8，`fontSize` 15。不要收到 16/10。
7. **皮肤**：dark、黑底、固定 `classDef` 配色（见 mermaid_better.md）。

出图前先读 mermaid_better.md 的模板和「好 vs 坏」。
