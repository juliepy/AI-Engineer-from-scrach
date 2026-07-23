# 步骤 3 · 拼接

对应逻辑图：`Out = head + Wrap(摘要消息) + tail`

| 文件 | 含义 |
|------|------|
| `拼接的context.md` | 压缩后发给主模型的完整 messages |
| `拼接的context.json` | 同上（机器可读） |
