# RELIABILITY.md

這份檔案定義系統如何證明自己健康且可重啟。

## 標準路徑

- Bootstrap：`[command]`
- Verification：`[command]`
- 啟動應用程式或服務：`[command]`
- 除錯或檢查執行階段：`[command]`

## 必需執行信號

- 啟動與關鍵流程的結構化日誌
- 關鍵服務的健康檢查
- 在可用時，為慢路徑提供 trace 或 timing 資料
- 針對可恢復的失敗，提供使用者可見的錯誤狀態

## 黃金旅程

- `[journey 1]`
- `[journey 2]`
- `[journey 3]`

每一條黃金旅程都應該有可重複的驗證路徑與明確的失敗信號。

## 可靠性規則

- 如果系統之後無法乾淨重啟，功能就不算完成。
- 執行階段失敗應該能從儲存庫內的信號診斷。
- 如果某類失敗模式重複出現，就新增對應的 benchmark 或 guardrail。
- cleanup 是可靠性的一部分。
