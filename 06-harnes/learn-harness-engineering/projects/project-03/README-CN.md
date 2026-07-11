# Project 03: Multi-Session Continuity with Scope Control

评估进度记录、会话交接、显式范围控制和验证门控是否能提高跨重启交付准确性。

## 目录说明

| 目录 | 含义 |
|------|------|
| `starter/` | **起点**——基于 P2 solution，文档分块、元数据提取、索引状态、带引用问答待实现。它有 starter 版 `feature_list.json`，但缺少完整的重启/交接 harness（`init.sh`、`session-handoff.md`、`claude-progress.md`、clean-state checklist）。 |
| `solution/` | **参考实现**——所有功能已实现，AGENTS.md 包含"一次一个功能"策略，并补齐重启/连续性产物。 |

## 使用方法

```sh
cd starter
npm install
# 至少跑两个 agent 会话。中途停止一次，再只靠仓库状态恢复。
# 观察 agent 是否保持范围并更新 feature_list.json。

cd ../solution
npm install
# 检查完成后的连续性产物和功能证据
```

## 具体任务对应关系

Project 03 starter 不是空应用，而是 Project 02 加上未完成的索引和带引用问答。按一次一个功能完成：

| 功能 / 产物 | starter 状态 | solution 证据 |
|------|------|------|
| 文档分块 | `IndexingService` 需要段落感知的 chunk 创建 | `indexing-service.ts`, `feature_list.json` 的 `document-chunking` |
| 元数据提取 | 索引所需的文档元数据不完整 | `document-service.ts`, `DocumentDetail.tsx`, `metadata-extraction` |
| 索引状态 UI | 状态栏需要 indexed count / total chunks / 状态颜色 | `StatusBar.tsx`, `App.tsx`, `indexing-status-ui` |
| 带引用问答 | QA 必须返回 chunk 引用、摘录和置信度 | `qa-service.ts`, `QuestionPanel.tsx`, `grounded-qa` |
| 连续性 harness | starter 缺少最终重启/交接产物 | `init.sh`, `session-handoff.md`, `claude-progress.md`, `clean-state-checklist.md` |

不要把这个项目理解成泛泛的"多会话"练习；产品切片是索引 + 带引用问答，harness 切片是可重启的进度追踪。

## 本项目涉及的功能

- 文档分块（段落感知，~500 字符）
- 元数据提取（词数、行数、段落数）
- 索引状态在 UI 中显示
- 基础问答流程，带来源引用

## 对应课件

- [Lecture 05: 保持跨会话上下文](../../docs/en/lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md)
- [Lecture 06: 每次会话前先初始化](../../docs/en/lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
