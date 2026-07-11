# Project 04. 用執行回饋修正代理的行為

> 相關講義：[L07. 給 agent 劃清每次任務的邊界](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [L08. 用功能清單約束 agent 該做什麼](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> 本篇範本檔案：[templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh-TW/resources/templates/)

## 你要做什麼

前三個專案關注的是「讓代理把任務做完」。這個專案關注的是「出了問題怎麼修」——而且不是你修，是讓代理自己透過執行時期訊號來修。

你要做兩件事。第一，給知識庫應用加上執行時期可觀測性，包括啟動日誌、匯入和索引的日誌、問答失敗時的使用者可見錯誤狀態。第二，在儲存庫中明確定義架構約束，讓代理不可能靜默地跨層違規（main / preload / renderer / services 之間的邊界）。

然後你會在程式碼裡植入一個執行時期 bug，讓代理去修。執行兩次，一次不給日誌和約束，觀察代理如何修正；一次給好日誌和架構規則，看差別。

## 使用倉庫內建專案

倉庫路徑：[`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| 目錄 | 內容 | 比較什麼 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | 以 Project 03 程式碼為基礎，但診斷能力較弱；存在一個種子缺陷，可能導致大型文件 chunking/索引失敗；也沒有架構檢查腳本。 | 沒有執行時期訊號時，定位根本原因需要多久、改動是否擴散。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | 結構化 logger、架構邊界文件與腳本、修復 chunking/索引邏輯，並補齊 [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md)。 | 有日誌與邊界檢查後，修復是否更快、更可控、可復現。 |

可供檢閱的具體檔案為 [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts)、[`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh)、[`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md) 和 [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts)。

## 用什麼工具

- Claude Code 或 Codex
- Git
- Node.js + Electron
- 日誌庫（如 `electron-log` 或簡單的 console 封裝）
- 結構化檢查工具（ESLint 自訂規則、guard 腳本、或測試）

## Harness 機制

執行時期回饋 + 範圍控制 + 漸進式索引

## 具體步驟

### 準備工作

1. 以 P03 完成後的程式碼為基礎，從同一個 commit 出發。
2. 建立兩個分支：`p04-baseline` 和 `p04-improved`。
3. 在兩個分支中植入同一個執行時期 bug（例如：索引時 chunk 大小讀取錯誤導致問答回傳空結果）。
4. 記錄 bug 的位置和表現，但不要告知代理 bug 所在。

### 第一次執行（弱 harness）

切換至 `p04-baseline` 分支。

1. 啟動代理，告知「問答功能回傳空結果，請修復」。
2. 儲存庫中沒有執行時期日誌，也沒有架構約束檔案。
3. 記錄代理花了多久找到根本原因、如何確認修復成效、修復過程中是否引入了新的層邊界違規。
4. 修復後重啟應用，確認是否能乾淨啟動。

### 第二次執行（強 harness）

切換至 `p04-improved` 分支。在啟動代理之前，先在儲存庫中準備好：

- **執行時期日誌**：啟動時輸出初始化步驟，匯入時輸出檔案數量和 chunk 結果，索引時輸出進度，問答失敗時輸出錯誤原因。
- **架構約束**：在 `AGENTS.md` 裡明確寫 Electron 四層邊界（main / preload / renderer / services），說明哪些呼叫路徑是允許的。用 ESLint 規則或 guard 腳本檢查違規。
- **乾淨狀態要求**：最終交付前必須能乾淨重啟。

然後啟動代理：

1. 先讓代理加上日誌和結構化檢查（這是任務的一部分）。
2. 然後告知「問答功能回傳空結果，請修復」。
3. 這次代理有日誌可以查看，有架構規則可以參照。
4. 記錄診斷速度、修復品質、是否引入了邊界違規。
5. 修復後重啟應用，確認乾淨啟動。

## 怎麼衡量結果

| 指標 | 說明 |
|------|------|
| 根因定位時間 | 從開始到代理準確描述 bug 根本原因 |
| 修復確認時間 | 從定位到驗證修復成功 |
| 邊界違規數 | 修復過程中引入的跨層違規次數 |
| 日誌有用性 | 日誌是否直接指向了失敗原因 |
| 乾淨重啟 | 修復後是否能乾淨重啟且無報錯 |

## 要交什麼

- 弱 harness 的除錯記錄：診斷過程、修復 diff、啟動證據
- 強 harness 的除錯記錄：同上，加上日誌和架構約束檔案
- 結構化檢查產物（lint 規則、guard 腳本、或測試檔案）
- 一份對比筆記：重點比較診斷速度和修復健壯性

## 對應講義

- [Lecture 11 — 為什麼可觀測性屬於 harness 的一部分](../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md)
- [Lecture 12 — 為什麼每個工作階段都必須留下乾淨狀態](../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
