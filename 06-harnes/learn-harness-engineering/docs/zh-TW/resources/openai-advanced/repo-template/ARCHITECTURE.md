# ARCHITECTURE.md

這份檔案是系統的頂層地圖。內容應保持簡短，並在需要時指向更深入的文件。

## 系統形態

- 產品： `[替換成產品名稱]`
- 主要使用者流程： `[替換成核心流程]`
- 執行介面： `[desktop / web / cli / services / workers]`
- 產品行為的真相來源： `docs/product-specs/`

## 領域地圖

| 領域 | 負責內容 | 主要入口點 | 對應規格 |
|------|----------|------------|----------|
| `[domain-a]` | `[負責範圍]` | `[modules / routes / commands]` | `[spec path]` |
| `[domain-b]` | `[負責範圍]` | `[modules / routes / commands]` | `[spec path]` |

## 分層模型

使用固定方向的分層模型，避免代理臨時拼出任意架構：

`Types -> Config -> Repo -> Service -> Runtime -> UI`

橫切關注點應透過明確的 provider 或 adapter 邊界進入，不要直接跨層延伸。

## 硬性相依規則

- 低層不得依賴高層。
- UI 不得繞過 runtime 或 service 契約。
- 資料存取必須透過 repositories 或等價的 adapter 進入。
- 共用 utilities 必須維持通用性，不得累積領域邏輯。
- 新增相依時，應在對應的計畫或設計文件中說明理由。

## 橫切介面

| 關注點 | 核准邊界 | 備註 |
|--------|----------|------|
| Logging and tracing | `[provider / utility path]` | `[僅限結構化記錄，不可臨時使用 console]` |
| Auth | `[provider path]` | `[token / session 規則]` |
| External APIs | `[client or provider path]` | `[rate limit / retry 原則]` |
| Feature flags | `[flag boundary]` | `[歸屬]` |

## 目前熱點

- `[代理最難安全修改的區域]`
- `[邊界薄弱或測試脆弱的區域]`

## 變更檢查清單

當你改動與架構相關的程式碼時：

1. 如果領域地圖或允許的邊界改變，就更新這份檔案。
2. 如果背後的設計理由改變，就更新 `docs/design-docs/` 內相關的設計文件。
3. 如果某條規則應該用機械方式執行，就新增或更新可執行檢查。
