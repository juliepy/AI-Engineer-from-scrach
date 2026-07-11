# Project 05. 讓代理自己檢查自己做得對不對

> 相關講義：[L09. 防止 agent 提前宣告完成](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [L10. 跑通完整流程才算真正驗證](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> 本篇範本檔案：[templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh-TW/resources/templates/)

## 你要做什麼

前四個專案裡，「檢查做得對不對」這件事要麼是你手動做的，要麼是靠檔案規則強制執行的。這個專案要讓代理自行檢查。

方法是角色分離。以前是同一個代理既寫程式碼又判斷品質。現在拆開，生成者代理負責實作，評估者代理負責審查。更進一步，還可以加一個負責規劃的角色（規劃者）。你要執行三次，看每加一層角色分離，結果好多少。

選一個實質性的功能升級（如多輪對話歷史、引用面板重新設計、文件集合與篩選），三次都做同一個升級，唯一變數是 harness 的角色分工。

## 使用倉庫內建專案

倉庫路徑：[`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| 目錄 | 內容 | 比較什麼 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | 以 Project 04 的應用為基礎，尚未實作 ConversationHistory（多輪對話歷史）升級。 | 若你要自己重跑三種變體，從這裡開始。 |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | 單角色：同一個代理負責規劃/實作/自查。 | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md) 1.6/5 分與缺陷清單。 |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | 生成者 + 評估者：有修訂與回饋證據。 | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md) 3.3/5 分與修訂記錄。 |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | 規劃者 + 生成者 + 評估者：有 sprint contract。 | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) 與 [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md) 4.9/5 分。 |

檢入的功能為多輪問答對話歷史。在三個變體中保持此功能不變，使唯一的變數為角色分離。

## 用什麼工具

- Claude Code 或 Codex（用於生成和規劃角色）
- 同一個或另一個代理實例（用於評估角色）
- 評估量表（參考 `docs/zh-TW/resources/templates/evaluator-rubric.md`）
- Sprint contract 範本（參考 `docs/en/lectures/lecture-11-why-observability-belongs-inside-the-harness/code/sprint-contract.md`）

## Harness 機制

自我驗證 + 有依據的問答 + 以證據為基礎的完成判定

## 具體步驟

### 準備工作

1. 以 P04 完成後的程式碼為基礎，從同一個 commit 出發。
2. 建立三個分支：`p05-single`、`p05-gen-eval`、`p05-plan-gen-eval`。
3. 選定一個功能升級，寫清楚驗收標準。三次執行的功能範圍和驗收標準完全一致。
4. 制定評估量表，評分維度至少包括：正確性、可靠性、可維護性、用戶體驗。

### 第一次執行（弱 harness — 單角色）

切到 `p05-single` 分支。

1. 一個代理包攬規劃、實作、自查。
2. 沒有外部評估量表，代理自行判斷品質。
3. 記錄最終產出和未解決的缺陷。

### 第二次執行（強 harness — 生成者 + 評估者）

切到 `p05-gen-eval` 分支。

1. 生成者和評估者先用 sprint contract 對齊：做什麼、怎麼驗證、什麼不算在範圍內。
2. 生成者實作功能。
3. 評估者用評估量表評分，並回饋問題。
4. 生成者根據回饋修改。至少經過一輪修訂。
5. 記錄評估者抓住了多少缺陷、修訂了多少內容。

### 第三次執行（更強 harness — 規劃者 + 生成者 + 評估者）

切到 `p05-plan-gen-eval` 分支。

1. 規劃者先拆解任務、定義步驟和依賴關係。
2. 生成者按規劃實作。
3. 評估者用同一份評估量表打分。
4. 至少經過一輪修訂。
5. 記錄規劃是否減少了返工。

### 評估者調優

評估者不是一次就能用好的。初始版本的評估者可能會「發現問題，卻自行說服自己通過」。你需要：

1. 讓評估者給一個已完成的 sprint 評分。
2. 與你自己的判斷相比對。
3. 哪裡有分歧，就把量表寫得更具體。
4. 重新執行評估者，檢查對齊程度。
5. 重複 3 至 5 輪，直到評估者的判斷與你的判斷大致一致。記錄每一輪調優的內容。

## 怎麼衡量結果

| 指標 | 說明 |
|------|------|
| 範圍定義品質 | 編碼前的任務拆解清晰度 |
| 缺陷檢出數 | 交付前被評估者抓到的缺陷數量和嚴重程度 |
| 量表評分 | 各維度的得分（正確性、可靠性、可維護性、UX） |
| 返工量 | 評估回饋後需要重做的比例 |
| 最終健壯性 | 升級後功能在實際執行中的穩定程度 |
| 評估者調優輪數 | 評估者判斷與你對齊需要的迭代次數 |
| Sprint contract 效果 | 合約是否減少了評估中的模糊地帶 |

## 要交什麼

- Sprint contract 文件
- 評估者調優日誌（每輪改了什麼、為什麼改）
- 單角色執行記錄：提示詞、日誌、可執行證據
- 生成者＋評估者執行記錄：含量表評分和修訂記錄
- 規劃者＋生成者＋評估者執行記錄：含規劃文件、量表評分、修訂記錄
- 一份對比筆記：品質提升幅度和協調成本

## 對應講義

- [Lecture 09 — 為什麼 agent 總是過早宣佈勝利](../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md)
- [Lecture 10 — 為什麼端到端測試能改變結果](../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
- [Lecture 11 — 為什麼可觀測性屬於 harness 的一部分](../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md)
