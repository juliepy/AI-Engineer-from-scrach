<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills（技能集）

本目录包含 Learn Harness Engineering 项目的可复用 AI agent 技能。每个技能都是一个自包含的提示词模板，可被 AI 编程智能体（Claude Code、Codex、Cursor、Windsurf 等）加载以执行专业任务。

## 可用技能

### harness-creator

面向 AI 编程智能体的生产级 harness 工程技能。帮助创建、评估和改进 agent harness 文件（AGENTS.md、功能清单、验证工作流、会话连续性机制）。

- **7 个参考模式**：记忆持久化、技能运行时、上下文工程、工具注册、多智能体协调、生命周期与引导、陷阱
- **模板**：AGENTS.md/CLAUDE.md、feature-list.json、init.sh、progress.md、session-handoff.md
- **脚本**：脚手架生成、校验、HTML 评估报告、结构化 benchmark
- **10 个内置评估测试用例**

详见 [harness-creator/README.md](harness-creator/README.md)。

## harness-creator 的开发过程

`harness-creator` 技能基于 **skill-creator** 方法论开发——这是 Anthropic 官方提供的元技能，用于创建、测试和迭代改进 agent 技能。skill-creator 提供了结构化的工作流（起草 → 测试 → 评估 → 迭代），内置评估运行器、评分器和基准查看器。

- **skill-creator 来源**：[anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Anthropic Claude Code 技能文档**：[anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)

## 目录结构

```
skills/
├── README.md                    # 英文说明
├── README-CN.md                 # 中文说明（本文件）
├── README-ZH-TW.md              # 繁体中文说明
├── README-JA.md                 # 日文说明
├── README-ES.md                 # 西班牙文说明
├── README-FR.md                 # 法文说明
├── README-AR.md                 # 阿拉伯文说明
├── README-VI.md                 # 越南文说明
├── README-DE.md                 # 德文说明
└── harness-creator/             # Harness 工程技能
    ├── SKILL.md                 # 主技能定义
    ├── SKILL.md.en              # 英文版
    ├── README.md                # 详细文档
    ├── metadata.json            # 技能元数据与触发词
    ├── agents/                  # 技能 UI 元数据
    ├── scripts/                 # 脚手架、校验和 benchmark 辅助脚本
    ├── evals/                   # 测试用例
    ├── templates/               # 脚手架模板
    └── references/              # 深入的模式参考文档
```

## 技能的工作方式

每个技能遵循标准结构：

1. **SKILL.md** — 入口文件。包含 YAML frontmatter（name、description，用于触发）和 Markdown 指令。
2. **references/** — 按需加载到上下文中的补充文档。
3. **templates/** — 技能为用户生成的起始模板。

技能采用渐进式展开 — agent 首先只看到名称 + 描述，触发后加载完整的 SKILL.md 正文，仅在需要时读取附带的资源文件。

## 安全审计

本目录中的所有文件均已通过安全审计：

- 无后门、隐藏 URL 或编码载荷
- 无数据泄露或硬编码凭证
- 无命令注入漏洞
- 脚本仅使用 Node.js 内置模块
- 生成的 `init.sh` 运行检测到的项目验证命令

## 许可证

MIT
