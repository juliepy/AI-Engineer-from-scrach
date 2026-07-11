# Project 02. 讓代理看懂專案、銜接上次的工作

> 相關講義：[L03. 讓程式碼儲存庫成為唯一的事實來源](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [L04. 把指令拆分到不同檔案裡](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> 本篇範本檔案：[templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh-TW/resources/templates/)

## 你要做什麼

P01 證明了準備規則有用。但 P01 的任務一次工作階段就完成了。真實開發不是這樣的——你昨天做了一半，今天開啟新工作階段，代理得從儲存庫狀態中釐清「做了什麼、尚未完成什麼、接下來要做什麼」。

這個專案要求你為儲存庫加上「可讀性」，讓一個全新的代理開啟儲存庫後，能快速理解專案結構、知道目前進度、銜接上次的工作。具體任務是給知識庫應用加上三個功能，包括文件匯入、文件詳情頁面、匯入後的本地持久化。這些功能必須跨至少兩個代理工作階段完成。

你需要執行兩次。第一次不給代理任何幫助，看它在第二個工作階段裡要花多久才能「銜接上」。第二次提前放好 `ARCHITECTURE.md`、`PRODUCT.md`、`session-handoff.md`，讓它快速對齊脈絡。

## 使用倉庫內建專案

倉庫路徑：[`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| 目錄 | 內容 | 比較什麼 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | 基於 Project 01 解答版本的程式碼，但匯入/詳情/持久化仍未完整；文件較少，且缺少 `session-handoff.md`。 | 開啟新工作階段時，代理需要重新探索多少才能銜接進度。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | 同一產品切片已完成，並在 [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) 下補齊核心文件（以及 [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json)、[`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md)）等可接手產物。 | 只依靠儲存庫狀態，能否快速續寫而不靠口頭脈絡。 |

產品功能包含文件匯入、完整文件詳情與內容載入，以及重啟後的資料持久化。harness 功能是可供工作階段交接的可讀工作區。

## 用什麼工具

- Claude Code 或 Codex（和 P01 保持一致）
- Git
- Node.js + Electron
- 文字編輯器（撰寫文件用）

## Harness 機制

可讀的代理工作區 + 持久化狀態檔案

## 具體步驟

### 準備工作

1. 以 P01 完成後的程式碼為基礎，從同一個 commit 出發。
2. 建立兩個分支：`p02-baseline` 和 `p02-improved`。
3. 列出要實作的三個功能：文件匯入流程、文件詳情檢視、文件持久化。兩條分支任務範圍完全一致。

### 第一次執行（弱 harness）

切到 `p02-baseline` 分支。

**工作階段 A：**

1. 啟動代理，只提供任務描述，不提供架構文件，不提供進度檔案。
2. 刻意在功能完成之前結束工作階段（例如只完成文件匯入）。
3. 不撰寫任何交接檔案。直接結束。

**工作階段 B：**

1. 開啟一個全新的代理工作階段。
2. 只告知「繼續開發」，不提供額外脈絡。
3. 記錄代理花了多久才做出第一個有意義的程式碼修改。
4. 記錄代理哪些時候在「重新發現」本來已經知道的東西。

### 第二次執行（強 harness）

切換至 `p02-improved` 分支。在第一個工作階段之前，先在儲存庫中準備好：

- `ARCHITECTURE.md`：描述專案結構、Electron 各層職責、資料流
- `PRODUCT.md`：描述產品功能範圍和目前階段目標
- `AGENTS.md`：啟動命令、工作規則、驗證方式
- `init.sh`：一鍵恢復可執行狀態

**工作階段 A：**

1. 啟動代理，讓它開始工作。
2. 同樣在功能完成之前停止。
3. **這次要求代理更新 `session-handoff.md`**：記錄做了什麼、沒做什麼、下一步是什麼。

**工作階段 B：**

1. 開啟一個全新的代理工作階段。
2. 讓代理讀取 `session-handoff.md` 和 `feature_list.json`，然後繼續。
3. 同樣記錄銜接速度和重複工作比例。

## 怎麼衡量結果

| 指標 | 說明 |
|------|------|
| 工作階段 B 銜接時間 | 從開始到第一個有效程式碼修改的時間 |
| 重新發現次數 | 代理重新瞭解架構、命令、狀態等既有資訊的次數 |
| 交接檔案品質 | 交接記錄是否完整、準確、可操作 |
| 重複工作比例 | 工作階段 B 中有多少工作量是在重複工作階段 A 已做過的事 |
| 最終完成狀態 | 三個功能是否全部完成 |

## 要交什麼

- 弱 harness 的工作階段 A + B 日誌/對話記錄
- 強 harness 的工作階段 A + B 日誌/對話記錄
- 兩次執行中產生的交接檔案
- 一份對比筆記：重點比較銜接速度和脈絡恢復品質

## 對應講義

- [Lecture 03 — 為什麼倉庫必須成為唯一事實來源](../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md)
- [Lecture 04 — 為什麼一個大而全的指令檔案不行](../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
- [Lecture 05 — 為什麼長任務會遺失連續性](../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md)
