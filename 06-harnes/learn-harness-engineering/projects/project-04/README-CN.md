# Project 04: Runtime Feedback and Structural Control

引入运行时可观测性和结构化边界检查，同时调试一个植入的运行时缺陷。

## 目录说明

| 目录 | 含义 |
|------|------|
| `starter/` | **起点**——基于 P3 solution，新增日志、结构化边界功能待实现。`IndexingService` 中植入了一个隐蔽 bug：超过 1000 字符的文件可能产生无效/空分块。没有架构检查脚本，也没有最终 clean-state checklist。 |
| `solution/` | **参考实现**——结构化日志模块、架构边界检查脚本、植入 bug 已修复。 |

## 使用方法

```sh
cd starter
npm install
# 1. 观察 agent 能否通过日志定位 bug
# 2. 导入一个大文件，观察分块结果是否异常

cd ../solution
npm install
# 对比：结构化日志如何加速问题诊断
```

## 具体任务对应关系

Project 04 是调试和护栏练习。starter 已有 Project 03 的产品切片，但运行时信号不足，并且植入了分块缺陷。应该先让 agent 看见足够诊断证据，再修 bug。

| 功能 / 产物 | starter 状态 | solution 证据 |
|------|------|------|
| 结构化日志 | 没有共享 logger service | `src/services/logger.ts`，以及 `main.ts`、`ipc-handlers.ts`、services 中的日志调用 |
| 导入/索引诊断 | 运行输出难以定位失败 | 导入、索引开始/完成、QA 失败路径的日志 |
| 架构边界 | 没有脚本检查 renderer/main/service 越界 | `scripts/check-architecture.sh`, `docs/ARCHITECTURE.md`, AGENTS 边界规则 |
| 植入分块 bug | 大文件可能产生无效/空 chunk | 修复后的 `src/services/indexing-service.ts` |
| 干净交接 | starter 没有最终清单 | `clean-state-checklist.md` |

修复前后都用长文档复现一次。合格解法要有诊断证据，而不只是声称通过。

## 本项目涉及的功能

- 启动日志
- 导入和索引日志
- 可见的问答失败路径
- main / preload / renderer / services 层的显式边界
- 调试一个植入的运行时缺陷

## 对应课件

- [Lecture 07: 给代理划定清晰的任务边界](../../docs/en/lectures/lecture-07-why-agents-overreach-and-under-finish/index.md)
- [Lecture 08: 用功能列表约束代理行为](../../docs/en/lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
