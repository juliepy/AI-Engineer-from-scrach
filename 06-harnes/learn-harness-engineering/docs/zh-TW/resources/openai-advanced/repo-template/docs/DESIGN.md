# DESIGN.md

這份檔案是設計文件的入口。內容要保持簡短，並把更詳細的內容導向
`docs/design-docs/` 下面的具體檔案。

## 目的

記錄應該跨越單次聊天、單個 sprint 與單個 reviewer 記憶而持續存在的產品與系統設計決策。

## 什麼時候先看它

- 你需要理解目前的設計理念
- 你準備引入新模式
- 你要知道哪些設計決策已經定案，哪些仍然開放

## 核心設計文件

- `docs/design-docs/index.md`：accepted、proposed 與 deprecated 文件索引
- `docs/design-docs/core-beliefs.md`：專案層級的代理優先核心信念

## 設計規則

- 設計文件要保持簡短且維持最新。
- 每個決策領域盡量只對應一份文件。
- 當某個改動依賴設計文件時，要在 plan 和 spec 裡明確連結。
- 如果某條設計規則已成為執行上的關鍵要求，就把它升級成自動化檢查，或更新到 `ARCHITECTURE.md`。
