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

本目錄包含 Learn Harness Engineering 專案的可重用 AI agent 技能。每個技能都是自包含的提示範本，可由 Claude Code、Codex、Cursor、Windsurf 等 AI 編程 agent 載入，以執行特定任務。

## 可用技能

### harness-creator

面向 AI 編程 agent 的生產級 harness engineering 技能。它協助建立、評估與改進 agent harness 檔案，例如 AGENTS.md、功能清單、驗證工作流與跨會話延續機制。

- **7 個參考模式**：記憶持久化、技能執行期、上下文工程、工具註冊、多 agent 協調、生命週期與啟動、常見陷阱
- **範本**：AGENTS.md/CLAUDE.md、feature-list.json、init.sh、progress.md、session-handoff.md
- **腳本**：腳手架生成、校驗、HTML 評估報告、結構化 benchmark
- **10 個內建 eval 測試案例**

完整文件請見 [harness-creator/README.md](harness-creator/README.md)。

## harness-creator 的建立方式

`harness-creator` 使用 **skill-creator** 方法論建立。這是 Anthropic 用於建立、測試與迭代 agent skills 的官方 meta-skill，提供 draft → test → evaluate → iterate 的結構化流程。

## 技能如何運作

每個技能遵循標準結構：

1. **SKILL.md** — 入口檔案，包含 YAML frontmatter 與給 agent 的 Markdown 指令。
2. **references/** — 需要時載入上下文的補充文件。
3. **templates/** — 技能可產生的起始範本。

技能採用 progressive disclosure：agent 一開始只看到名稱與描述，觸發後才載入完整 SKILL.md，並只在必要時讀取附帶資源。

## 安全審計

本目錄中的檔案已完成安全檢查：

- 無後門、隱藏 URL 或編碼 payload
- 無資料外洩或硬編碼憑證
- 無命令注入漏洞
- 腳本僅使用 Node.js 內建模組
- 生成的 `init.sh` 會執行偵測到的專案驗證命令

## 授權

MIT
