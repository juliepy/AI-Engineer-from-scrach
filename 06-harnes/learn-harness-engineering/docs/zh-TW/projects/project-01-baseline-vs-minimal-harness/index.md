# Project 01. 只寫提示詞讓代理做，和定好規則再讓它做，差多少

> 相關講義：[L01. 模型能力強，不等於執行可靠](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [L02. Harness 到底是什麼](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> 本篇範本檔案：[templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh-TW/resources/templates/)

## 你要做什麼

用 Electron 搭一個最簡的知識庫應用殼子——能啟動視窗、左側顯示文件清單、右側顯示問答面板、本地有一個資料目錄。任務本身不複雜，複雜的是你如何讓代理完成它。

你需要執行兩次。第一次只給一段提示詞，什麼都不準備，看代理能做到什麼程度。第二次提前在儲存庫裡放好 `AGENTS.md`、`init.sh`、`feature_list.json`，用結構化的方式告訴代理該做什麼、怎麼驗證、什麼時候算做完。然後對比兩次結果。

課程場景使用一小段準備或重新探索時間作為示例，不依賴固定測量值。

## 使用倉庫內建專案

倉庫路徑：[`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| 目錄 | 內容 | 怎麼用 / 比較什麼 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | 弱 harness 版本。只有 [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) 作為任務描述，沒有 `AGENTS.md` 或 `feature_list.json`。 | 把提示詞交給程式碼代理，衡量它在沒有額外結構時完成了什麼。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | 相同的產品切片，但加入明確的 harness 產物：[`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md)、[`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md)、[`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh)、[`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json)、[`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md)。 | 對照規則與驗證證據如何把同一任務變得可執行、可驗收。 |

四個具體功能是視窗啟動、文件清單、問答面板、本地資料目錄建立。每個功能的預期證據請看 `solution/feature_list.json`。

## 用什麼工具

- Claude Code 或 Codex（選一個，兩次都用同一個）
- Git（管理分支和對比）
- Node.js + Electron（專案技術堆疊）
- 一個計時器（記錄每次執行時期間）

## Harness 機制

最小 harness：`AGENTS.md` + `init.sh` + `feature_list.json`

## 具體步驟

### 準備工作

1. 從一個乾淨的 commit 出發，記錄 commit hash。
2. 建立兩個分支：`p01-baseline` 和 `p01-improved`。
3. 準備一段相同的任務提示詞，內容為「用 Electron 做一個知識庫應用，視窗左側是文件清單區域，右側是問答面板區域，應用需要建立並使用本地資料目錄。」

### 第一次執行（弱 harness）

切到 `p01-baseline` 分支。

1. 只用上述提示詞啟動代理。
2. 不提供 `AGENTS.md`，不提供啟動腳本，不提供驗收標準。
3. 設定相同的時間上限和輪次上限（建議 30 分鐘 / 20 輪）。
4. 代理停止後，執行 `npm start`（或對應啟動命令），確認應用是否能正常啟動。
5. 記錄：終端輸出、關鍵 diff、代理的最終總結。
6. **不要手動修改程式碼**。無法啟動就如實記錄。

### 第二次執行（強 harness）

切換至 `p01-improved` 分支。在啟動代理之前，先在儲存庫裡準備好：

- `AGENTS.md`：說明專案結構、啟動命令、Electron 層邊界規則
- `init.sh`：一鍵恢復可執行狀態（`npm install && npm start`）
- `feature_list.json`：列出四個功能點及其完成狀態

然後使用與第一次相同的提示詞啟動代理，同樣的時間上限和輪次上限。代理停止後，執行 `./init.sh`，記錄結果。

## 怎麼衡量結果

| 指標 | 說明 |
|------|------|
| 完成狀態 | 完全完成 / 部分完成 / 失敗 |
| 首次成功啟動時間 | 從開始到 `npm start` 第一次成功執行 |
| 重試次數 | 中間需要人工介入幾次才能成功啟動 |
| 遺漏項 | 代理宣告完成時仍有哪些功能尚未實作 |
| 過早停止 | 代理是否在應用尚無法執行時便宣告完成 |

## 要交什麼

- 弱 harness 執行記錄：提示詞、日誌/對話記錄、最終 diff、啟動證據
- 強 harness 執行記錄：同上，加上你準備的 harness 檔案
- 一份對比筆記（1-2 頁）：兩次執行的差異、資料、結論

## 對應講義

- [Lecture 01 — 為什麼強 agent 仍然失敗](../../lectures/lecture-01-why-capable-agents-still-fail/index.md)
- [Lecture 02 — harness 到底是什麼](../../lectures/lecture-02-what-a-harness-actually-is/index.md)
- [Lecture 06 — 為什麼初始化需要單獨一個階段](../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
