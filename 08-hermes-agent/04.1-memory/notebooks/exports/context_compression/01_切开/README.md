# 步骤 1 · 切开（Split）

对应逻辑图：`messages → Split → head / middle / tail`

- protect_first_n = 3  ← system + 首轮 user/assistant（不只是 system）
- protect_last_n = 2
- head=3 | middle=12 | tail=2

| 文件 | 含义 |
|------|------|
| `system_prompt.md` | 仅 system / MEMORY（head 的子集） |
| `head.md` | protect head = system + 前几轮对话 |
| `middle.md` | 待摘要的中间轮次 |
| `tail.md` | protect tail（原样保留） |
