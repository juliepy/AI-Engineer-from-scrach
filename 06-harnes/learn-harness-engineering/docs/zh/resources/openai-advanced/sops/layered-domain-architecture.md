# SOP：分层领域架构

当 agent 反复跨层乱连、在不同层重复逻辑、或者几轮会话后代码越来越难审时，就用这份 SOP。

## 目标

把领域边界写清楚、立起来、能执行，让 agent 在高速度下也不至于悄悄把结构做烂。

## 目标模型

在一个业务领域内部，优先使用这条单向流：

`Types -> Config -> Repo -> Service -> Runtime -> UI`

跨领域关注点通过明确的 provider 或 adapter 进入。共享 utils 保持在领域之外，不能慢慢长成业务逻辑垃圾场。

## 建设检查清单

- 在 `ARCHITECTURE.md` 里列清当前 domains。
- 在 `ARCHITECTURE.md` 里写清允许的依赖方向。
- 记录 auth、telemetry、外部 API 等 cross-cutting interface。
- 为当前最难处理的边界违规写一条短说明。
- 决定哪些规则应该升级成 lint、test 或 script。

## 执行 SOP

1. 先给代码库画 domain map，再谈实现风格。
2. 对每个 domain，明确允许的 layer sequence。
3. 找出所有横切关注点，并把它们改走 provider 或 adapter。
4. 把含糊的 shared logic 重新放回所属 domain，或抽成真正通用的 utils。
5. 把规则写进 `ARCHITECTURE.md`。
6. 先为代价最高的一类违规补一个可执行 guardrail。
7. 改完后更新质量评分。

## 完成定义

- 一个全新的 agent 能判断某个改动应该落在哪一层。
- UI 不再直接连 repo 或外部副作用。
- 横切能力都有明确入口。
- 至少一条重要边界已经被机械执行。

## 需要同步更新的仓库工件

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- 如果设计理由变了，更新 `docs/design-docs/`
- `docs/PLANS.md` 或当前 active execution plan
