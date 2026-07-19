# 步骤 2 · middle 摘要

对应逻辑图：`middle → 序列化 → 压缩 prompt → Aux LLM → summary → Wrap`

| 文件 | 含义 |
|------|------|
| `压缩prompt.md` | 发给辅助模型的完整 prompt |
| `摘要.md` | summarize_fn 纯输出（结构化摘要正文） |
| `包装后的摘要消息.md` | SUMMARY_PREFIX + 摘要 + END（插回用） |
