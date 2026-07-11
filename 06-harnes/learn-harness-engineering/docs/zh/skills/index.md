# Skills（技能集）

本目录包含课程附带的 AI agent 技能。每个技能都是自包含的提示词模板，可被 AI 编程智能体（Claude Code、Codex、Cursor、Windsurf 等）加载以执行专业任务。

## harness-creator

面向 AI 编程智能体的生产级 harness 工程技能。帮助创建、评估和改进五个核心 harness 子系统：指令、状态、验证、范围和会话生命周期。

### 它能做什么

- **从零创建 harness** — AGENTS.md、功能清单、验证工作流
- **改进已有 harness** — 五子系统评分 + 优先级改进建议
- **设计会话连续性** — 记忆持久化、进度跟踪、交接机制
- **应用生产级模式** — 记忆、上下文工程、工具安全、多智能体协调

### 快速开始

技能文件位于仓库的 [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator) 目录。

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

在 Claude Code 中使用时，将 `harness-creator/` 目录复制到你项目的技能路径下，或让 agent 直接读取 SKILL.md 文件即可。

### 参考模式

技能包含 7 个聚焦的模式参考文档：

| 模式 | 适用场景 |
|------|----------|
| 记忆持久化 | agent 在会话间遗忘项目知识 |
| Skill Runtime | 将可复用 workflow 打包成技能 |
| 上下文工程 | 上下文预算管理、按需加载、委托隔离 |
| 工具注册 | 工具安全、并发控制、权限管道 |
| 多智能体协调 | 并行化、专业化、研究员→实施者工作流 |
| 生命周期与引导 | 钩子、后台任务、初始化序列 |
| 常见陷阱 | 15 个容易踩坑的失败模式及修复方案 |

### 模板

技能附带开箱即用的模板：

- `agents.md` — AGENTS.md 脚手架，包含工作规则
- `feature-list.json` — JSON Schema + 功能列表示例
- `init.sh` — 标准初始化脚本
- `progress.md` — 会话进度日志模板
- `session-handoff.md` — 会话交接模板

### 脚本

技能也包含纯 Node.js 脚本，可用于脚手架生成、校验、HTML 评估报告与结构化 benchmark 报告。

### 开发过程

`harness-creator` 基于 **skill-creator** 方法论开发——这是 Anthropic 官方提供的元技能，用于创建、测试和迭代改进 agent 技能。skill-creator 提供了结构化的工作流（起草 → 测试 → 评估 → 迭代），内置评估运行器、评分器和基准查看器。

- **skill-creator 来源**：[anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Claude Code 技能文档**：[anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
