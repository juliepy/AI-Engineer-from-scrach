# Project 06: Runtime Observability and Debugging (Capstone)

课程毕业项目：构建并基准测试完整的 harness，执行清理循环验证质量可维护性。

## 目录说明

| 目录 | 含义 |
|------|------|
| `starter/` | **起点**——完整的产品代码，但 harness 被刻意削弱（只有基础 AGENTS.md，没有 feature_list.json、session-handoff、clean-state-checklist）。 |
| `solution/` | **参考实现**——最大 harness：所有产物文件齐全，质量文档评分高，包含基准测试脚本和清理扫描器。 |

## 使用方法

```sh
cd starter
npm install
# 运行应用并手动记录弱 harness 表现
# starter 故意不包含 benchmark.sh 或 cleanup-scanner.sh

cd ../solution
npm install
# 用完整 harness 跑同样的基准测试
# 执行清理循环
# 对比 quality-document.md 中的评分变化

# 运行基准测试
./scripts/benchmark.sh

# 运行清理扫描
./scripts/cleanup-scanner.sh
```

## 具体任务对应关系

Project 06 是完整产品 + 弱 harness 表面，与完整产品 + 强 harness 表面的对比。和前几个项目不同，starter 已经包含大部分产品功能，差距主要在代码周围的操作系统。

| 领域 | starter 状态 | solution 证据 |
|------|------|------|
| 产品行为 | 导入、索引、QA、历史、反馈、重置大多已存在 | 同功能，并有更强验证和持久化证据 |
| Harness 文件 | 只有基础 `AGENTS.md`，没有 `feature_list.json`、`session-handoff.md`、clean-state checklist | `AGENTS.md`, `CLAUDE.md`, `feature_list.json`, `init.sh`, `session-handoff.md`, `clean-state-checklist.md` |
| 质量追踪 | 初始 `quality-document.md` | 更高评分的 `quality-document.md`, `evaluator-rubric.md` |
| 基准测试 | 没有 benchmark / cleanup 脚本 | `scripts/benchmark.sh`, `scripts/cleanup-scanner.sh`, `scripts/check-architecture.sh` |
| 可靠性文档 | 文档较少 | `docs/ARCHITECTURE.md`, `docs/PRODUCT.md`, `docs/RELIABILITY.md` |

不要期待 starter 里有 solution 才提供的 benchmark 命令。弱 harness 运行使用手动基线记录，solution 运行使用已提交脚本。

## 本项目涉及的功能

- 导入文档
- 构建或刷新索引
- 带引用的问答
- 运行时反馈
- 可读的、可重启的仓库状态

## 对应课件

- [Lecture 11: 让代理的运行时可观测](../../docs/en/lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md)
- [Lecture 12: 每次会话都要留下干净的状态](../../docs/en/lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
