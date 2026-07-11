# Project 06. 搭建完整的代理工作環境

> 相關講義：[L11. 讓 agent 的執行過程可觀測](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [L12. 每次工作階段結束前都做好交接](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> 本篇範本檔案：[templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh-TW/resources/templates/)

## 你要做什麼

這是結業專案。把前五個專案學到的所有東西組裝起來，執行一次完整的基準測試，然後做一輪清理，驗證品質是可以持續維護的。

你要用一套固定的多功能任務集，涵蓋知識庫應用的完整產品切片，包括匯入文件、建構索引、附引用的問答、執行時期可觀測性、可讀可重啟的儲存庫狀態。先執行一次弱 harness 基線，再執行一次你組裝的最強 harness，然後做一輪清理和重新執行。最後還要做一次 harness 精簡實驗——刪掉一個組件，觀察結果是否變差，判斷哪些組件是真正有用的、哪些是多餘的開銷。

## 使用倉庫內建專案

倉庫路徑：[`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| 目錄 | 內容 | 怎麼用 / 比較什麼 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | 產品功能基本完整，但 harness 表面刻意削弱（只有基礎 [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md)，沒有 `feature_list.json` / `session-handoff.md` / `clean-state-checklist.md`，也沒有 benchmark/cleanup 腳本）。 | 起始版本刻意不包含基準測試腳本。手動記錄弱 harness 基線行為（錯誤定位速度、是否過早宣告完成等）。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | 最大化 harness：[`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md)、[`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md)、[`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json)、[`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh)、[`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md)、[`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md)、品質/評估文檔、benchmark 與 cleanup 腳本。 | 在 [`projects/project-06/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) 下跑 `./scripts/benchmark.sh` 與 `./scripts/cleanup-scanner.sh`，再對照品質文檔證據。 |

與前幾個專案不同，這份結業起始版本在產品功能上基本完整，主要缺口在於應用外圍的 harness 運作機制。

## 用什麼工具

- Claude Code 或 Codex
- Git
- Node.js + Electron
- 品質文件範本（`docs/zh-TW/resources/templates/quality-document.md`）
- 評估量表（`docs/zh-TW/resources/templates/evaluator-rubric.md`）
- 前五個專案積累的所有 harness 組件

## Harness 機制

完整 harness：所有機制 + 可觀測性 + 消融實驗

## 具體步驟

### 準備工作

1. 以 P05 完成後的程式碼為基礎，從同一個 commit 出發。
2. 建立兩個分支：`p06-baseline` 和 `p06-improved`。
3. 以品質文件範本為目前程式碼進行初始評分（每個產品領域和架構層的等級）。
4. 定義一套固定的基準任務集和評分表——在執行任何代理之前先定好，執行過程中不更改。

基準任務集至少包括：

- 匯入一篇文件
- 建構或重新整理索引
- 回答一個附引用的問題
- 查看執行時期日誌確認可觀測性
- 關閉再重新啟動後狀態仍保留

### 第一次執行（弱 harness）

切到 `p06-baseline` 分支。

1. 用課程早期階段的弱 harness（沒有完整交接檔案、沒有嚴格驗證、可觀測性不足）。
2. 以代理執行完整個基準任務集。
3. 立刻評分。記錄每個任務的完成狀態、重試次數、缺陷數。
4. 更新品質文件，記錄每個領域和層的等級變化。

### 第二次執行（強 harness）

切到 `p06-improved` 分支。

1. 用你在這門課裡組裝的最強 harness：交接檔案和啟動腳本、明確的範圍和驗證關卡、執行時期訊號和架構約束、評估者或多角色審查、品質文件追蹤。
2. 同樣的基準任務集，同樣的模型和預算。
3. 立刻評分，記錄結果，更新品質文件。

### 清理和重跑

在 `p06-improved` 分支上：

1. 做一輪清理：刪除無用程式碼、修正不清楚的文件、理順不穩定的執行路徑。
2. 清理後重新執行同樣的基準任務集，重新評分。
3. 更新品質文件。

比對三個快照的品質文件：基線、強 harness、清理後。

### Harness 精簡實驗

1. 從 `p06-improved` 分支中刪掉一個 harness 組件（比如刪掉 sprint contract，或者刪掉顯式範圍關卡）。
2. 重新執行基準任務集。
3. 如果結果沒變差，表示這個組件是多餘的開銷，可以去掉。
4. 如果結果變差了，表示這個組件是承重的，必須保留。
5. 記錄實驗結果。可以多試幾個組件。

## 怎麼衡量結果

| 指標 | 說明 |
|------|------|
| 基準完成率 | 基準任務集中成功完成的比例 |
| 重試次數 | 每個任務需要重試幾次 |
| 缺陷數 | 人工干預前發現的缺陷數量 |
| 清理工作量 | 清理花了多長時間、改了多少檔案 |
| 清理後可讀性和重啟成功率 | 清理後儲存庫的可維護程度 |
| 品質文檔等級變化 | 三個快照的等級對比 |
| Harness 精簡結果 | 哪些組件可以刪、哪些是承重的 |

## 要交什麼

- 品質文件的三個快照（基線、強 harness、清理後）
- 基線基準測試記錄：評分和證據
- 強 harness 基準測試記錄：評分和證據
- 清理執行記錄：清理前後評分變化
- Harness 精簡日誌：刪了什麼組件、基準結果、決定保留還是刪
- 最終結業總結：關鍵經驗教訓

## 對應講義

- [Lecture 01 — 為什麼強 agent 仍然失敗](../../lectures/lecture-01-why-capable-agents-still-fail/index.md)
- [Lecture 03 — 為什麼倉庫必須成為唯一事實來源](../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md)
- [Lecture 08 — 為什麼 feature list 是 harness 的基礎原語](../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
- [Lecture 11 — 為什麼可觀測性屬於 harness 的一部分](../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md)
- [Lecture 12 — 為什麼每個工作階段都必須留下乾淨狀態](../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
