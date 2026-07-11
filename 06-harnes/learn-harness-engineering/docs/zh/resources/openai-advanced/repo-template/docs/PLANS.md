# PLANS.md

这份文件定义执行计划如何创建、更新、完成和归档。

## 什么时候必须有 plan

当工作满足以下任一条件时，就创建 execution plan：

- 会跨越多个会话
- 会同时影响多个子系统
- 验证或上线风险不小
- 存在需要显式记录的开放决策

## 计划放哪

- `docs/exec-plans/active/`：当前正在驱动工作的计划
- `docs/exec-plans/completed/`：已完成但仍然要保留上下文的计划
- `docs/exec-plans/tech-debt-tracker.md`：延期处理的债务与 follow-up

## 最少要包含的部分

- 目标
- 范围与明确不做什么
- 验证路径
- 风险与 blocker
- 进度日志
- 开放决策

## 运行规则

- 一份 active plan 同一时间应该只有一个清晰的当前步骤。
- plan 要随着工作推进而更新，不要把它当成静态散文。
- 只要某个决策改变了实现方向，就记到 plan 里。
- 已完成的计划要移到 `completed/`，让后续 agent 仍然能发现历史上下文。
