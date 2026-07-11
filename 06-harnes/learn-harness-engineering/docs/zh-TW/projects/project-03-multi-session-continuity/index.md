# Project 03. 讓代理重啟後還能繼續執行

> 相關講義：[L05. 讓跨工作階段的任務保持脈絡連續](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [L06. 讓 agent 每次工作前先初始化](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> 本篇範本檔案：[templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh-TW/resources/templates/)

## 你要做什麼

P02 解決了「銜接」的問題，但代理銜接之後能否完整且正確地完成任務，則是另一回事。這個專案要你為代理加上範圍控制和驗證關卡。

你要實作的知識庫功能是文件分塊、元資料提取、索引進度顯示、附引用的問答流程。這些功能比前兩個專案複雜，代理更容易偏離目標，可能多做了不在範圍內的事，或是宣稱完成卻未通過驗證。

你需要一個 `feature_list.json`，每個功能有明確的狀態（failing / passing）。規則很簡單，一次只做一個功能，沒有可執行的驗證證據就不能標成 passing。執行兩次，一次不給這些約束，一次嚴格執行，觀察結果差距。

## 使用倉庫內建專案

倉庫路徑：[`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| 目錄 | 內容 | 比較什麼 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | 以 Project 02 程式碼為基礎，索引與 grounded QA 尚未完善；有初版 [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json)，但缺少最終的重啟/交接與乾淨狀態產物。 | 多次重啟或多功能任務下，代理是否偏移、是否遺失狀態。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | 完整的 chunking、metadata、indexing status、citation-based QA，並補齊 [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh)、[`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md)、[`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md)、[`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md)。 | 是否能做到“一次只做一個功能”，且每個功能都有可執行證據才標記通過。 |

本專案不是通用的「跨工作階段」練習。檢入的解答版本對應四個具體的產品功能：文件分塊、元資料提取、索引進度 UI 顯示，以及附引用的 grounded 問答。

## 用什麼工具

- Claude Code 或 Codex
- Git
- Node.js + Electron
- `feature_list.json`（範本參考 `docs/zh-TW/resources/templates/feature_list.json`）

## Harness 機制

進度日誌 + 工作階段交接 + 跨工作階段連續性 + 單次一功能驗證

## 具體步驟

### 準備工作

1. 以 P02 完成後的程式碼為基礎，從同一個 commit 出發。
2. 建立兩個分支：`p03-baseline` 和 `p03-improved`。
3. 定義四個功能：文件分塊、元資料提取、索引進度 UI 顯示、附引用的問答。兩條分支的功能定義完全一致。

### 第一次執行（弱 harness）

切到 `p03-baseline` 分支。

1. 啟動代理，給一段模糊的任務提示詞。
2. 不提供 `feature_list.json`，沒有狀態追蹤。
3. 不限制代理一次做幾個功能。
4. 沒有明確的驗證標準，代理自行宣告「完成了」便算數。
5. 執行結束後，手動確認每個功能是否確實可用。
6. 記錄哪些功能代理聲稱完成，但實際上未通過驗證。

### 第二次執行（強 harness）

切換至 `p03-improved` 分支。在啟動代理之前：

- 在儲存庫根目錄放好 `feature_list.json`，四個功能全部標為 `failing`。
- 在 `AGENTS.md` 裡寫明規則：一次只做一個功能；狀態只能從 `failing` 切到 `passing`，且必須有驗證證據。
- 準備好 `init.sh`。

然後啟動代理：

1. 代理開始工作，每完成一個功能必須更新 `feature_list.json` 並附上驗證證據（截圖、測試輸出等）。
2. 至少要有一個功能展示從 `failing` 到 `passing` 的完整轉換過程。
3. 問答功能的驗證必須檢查引用是否存在、引用是否相關，不能只看有沒有輸出。
4. 執行結束後歸檔所有驗證證據。

## 怎麼衡量結果

| 指標 | 說明 |
|------|------|
| 範圍漂移次數 | 代理做了功能清單之外的事的次數 |
| 虛假完成率 | 代理聲稱完成但驗證未通過的功能比例 |
| 驗證覆蓋率 | 有明確驗證證據的功能佔總功能的百分比 |
| 問答品質 | 引用是否存在、引用是否相關 |
| 重試次數 | 從開始到所有功能 passing 總共重試了幾次 |

## 要交什麼

- 弱 harness 執行記錄：提示詞、日誌、驗證結果
- 強 harness 執行記錄：`feature_list.json` 變更歷史、日誌、驗證證據
- 至少一個功能從 `failing` 到 `passing` 的轉換證據
- 一份對比筆記：重點看範圍紀律和完成準確度

## 對應講義

- [Lecture 07 — 為什麼 agent 總是做過頭、做不完](../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md)
- [Lecture 08 — 為什麼 feature list 是 harness 的基礎原語](../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
- [Lecture 09 — 為什麼 agent 總是過早宣佈勝利](../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md)
- [Lecture 10 — 為什麼端到端測試能改變結果](../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
