# Skills（技能集）

本目錄包含課程附帶的 AI 代理技能。每個技能都是自包含的提示詞範本，可被 AI 程式設計代理（Claude Code、Codex、Cursor、Windsurf 等）載入以執行專業任務。

## harness-creator

面向 AI 程式設計代理的生產級 harness 工程技能。幫助建立、評估和改進五個核心 harness 子系統，涵蓋指令、狀態、驗證、範圍和工作階段生命週期。

### 它能做什麼

- **從零建立 harness** — AGENTS.md、功能清單、驗證工作流
- **改進已有 harness** — 五子系統評分 + 優先級改進建議
- **設計工作階段連續性** — 記憶持久化、進度追蹤、交接機制
- **應用生產級模式** — 記憶、脈絡工程、工具安全、多智慧體協調

### 快速開始

技能檔案位於儲存庫的 [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator) 目錄。

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

在 Claude Code 中使用時，將 `harness-creator/` 目錄複製到你專案的技能路徑下，或讓 agent 直接讀取 SKILL.md 檔案即可。

### 參考模式

技能包含 7 個聚焦的模式參考檔案：

| 模式 | 適用場景 |
|------|----------|
| 記憶持久化 | 代理在工作階段間遺忘專案知識 |
| Skill Runtime | 將可重用 workflow 打包成技能 |
| 脈絡工程 | 脈絡預算管理、按需載入 |
| 工具註冊 | 工具安全、併發控制 |
| 多智慧體協調 | 平行化、專業化工作流 |
| 生命週期與引導 | 鉤子、背景任務、初始化序列 |
| 常見陷阱 | 15 個非顯然的失敗模式及修復方案 |

### 範本

技能附帶開箱即用的範本：

- `agents.md` — AGENTS.md 腳手架，包含工作規則
- `feature-list.json` — JSON Schema + 功能列表示例
- `init.sh` — 標準初始化腳本
- `progress.md` — 工作階段進度日誌範本
- `session-handoff.md` — 工作階段交接範本

### 腳本

技能也包含純 Node.js 腳本，可用於骨架生成、驗證、HTML 評估報告與結構化基準測試報告。

### 開發過程

`harness-creator` 基於 **skill-creator** 方法論開發——這是 Anthropic 官方提供的元技能，用於建立、測試和反覆改進 agent 技能。skill-creator 提供了結構化的工作流（起草 → 測試 → 評估 → 迭代），內建評估執行器、評分器和基準檢視器。

- **skill-creator 來源**：[anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Claude Code 技能檔案**：[anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
