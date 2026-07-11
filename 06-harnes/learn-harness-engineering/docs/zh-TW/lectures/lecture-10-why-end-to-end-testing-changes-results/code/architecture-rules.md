# Electron 架構規則

- Renderer 程式碼不得直接存取檔案系統。
- Preload 是 renderer 與 Electron main 之間唯一的橋樑。
- 檢索和索引邏輯應存在於服務模組中，而非 UI 元件中。
- 日誌應為結構化格式，並從服務邊界發出。
