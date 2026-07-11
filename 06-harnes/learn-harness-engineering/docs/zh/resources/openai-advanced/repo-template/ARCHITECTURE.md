# ARCHITECTURE.md

这份文件是系统的顶层地图。它应该保持简短，只提供最关键的结构信息，并把更深的内容指向其他文档。

## 系统形态

- 产品：`[替换成产品名]`
- 主用户流程：`[替换成核心流程]`
- 运行面：`[desktop / web / cli / services / workers]`
- 产品行为真相来源：`docs/product-specs/`

## 领域地图

| 领域 | 负责什么 | 主要入口 | 对应规格 |
|------|---------|---------|---------|
| `[domain-a]` | `[职责]` | `[模块 / 路由 / 命令]` | `[spec path]` |
| `[domain-b]` | `[职责]` | `[模块 / 路由 / 命令]` | `[spec path]` |

## 分层模型

用固定方向的分层模型，避免 agent 临场发明架构：

`Types -> Config -> Repo -> Service -> Runtime -> UI`

跨领域关注点应该通过明确的 provider 或 adapter 边界进入，而不是直接跨层穿透。

## 硬性依赖规则

- 低层不能依赖高层。
- UI 不能绕过 runtime 或 service 契约。
- 数据访问必须通过 repo 或等价 adapter 进入。
- 共享 util 必须保持通用，不能慢慢堆成领域逻辑垃圾桶。
- 新依赖要在对应 plan 或 design doc 里说明理由。

## 横切接口

| 关注点 | 允许的边界 | 备注 |
|-------|-----------|------|
| 日志与 tracing | `[provider / utility path]` | `[只允许结构化日志，不允许临时 console]` |
| Auth | `[provider path]` | `[token/session 规则]` |
| 外部 API | `[client 或 provider path]` | `[限流 / 重试原则]` |
| Feature flags | `[flag boundary]` | `[归属]` |

## 当前热点

- `[最难安全修改的区域]`
- `[边界最弱或测试最脆的区域]`

## 变更检查

当你修改了会影响架构的代码：

1. 如果领域地图或允许边界变了，就更新这份文件。
2. 如果背后的设计理由变了，就更新 `docs/design-docs/` 里的相关文档。
3. 如果规则应该机械执行，就补一个可执行检查。
