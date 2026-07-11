# OpenAI 高级 SOP

这些 SOP 把文章里的工作方式翻成可以直接参考、执行、改造的操作手册。

## 包含哪些 SOP

- [`layered-domain-architecture.md`](./layered-domain-architecture.md)：
  搭建显式分层与跨领域边界
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md)：
  把聊天、外部文档、脑内知识变成 repo-local 文档
- [`observability-feedback-loop.md`](./observability-feedback-loop.md)：
  给 agent 提供 logs、metrics、traces 与可重复的调试闭环
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md)：
  用浏览器自动化和快照反复验证 UI，直到 clean

## 怎么用

1. 先选和你当前瓶颈最匹配的 SOP。
2. 按检查清单补齐缺失工件或工具。
3. 把得到的规则编码回 `repo-template/` 里的文档。
4. 把反复出现的 review 评论升级成检查、脚本或 guardrail。

这些 SOP 不是让你机械照抄，而是为了让 harness 更可读、更可执行、更可复用。
