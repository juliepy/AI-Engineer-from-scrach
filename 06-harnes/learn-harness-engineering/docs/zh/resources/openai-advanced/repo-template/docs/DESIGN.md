# DESIGN.md

这份文件是设计文档入口。保持简短，把更细的内容路由到
`docs/design-docs/` 里的具体文件。

## 目的

记录那些应该跨越单次聊天、单个 sprint、单个 reviewer 记忆而持续存在的产品与系统设计决策。

## 什么时候先看它

- 你需要理解当前的设计哲学
- 你准备引入新模式
- 你要判断哪些设计已经定了，哪些还在开放状态

## 核心设计文档

- `docs/design-docs/index.md`：accepted / proposed / deprecated 文档索引
- `docs/design-docs/core-beliefs.md`：项目级 agent-first 核心信念

## 设计规则

- 设计文档要小而新。
- 一个决策领域尽量对应一份文档。
- 某个改动依赖设计文档时，要在 plan 和 spec 里显式链接它。
- 如果某条设计规则已经变成运行上的硬要求，就把它升级成自动化检查或更新到 `ARCHITECTURE.md`。
