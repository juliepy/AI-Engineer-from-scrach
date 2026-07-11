# OpenAI 高階資源包

這個資料夾把 OpenAI〈Harness engineering: leveraging Codex in an agent-first world〉一文中較具傾向性的儲存庫結構，整理成可直接複製的起步檔案。

當最小執行環境已經不夠用，而你的儲存庫開始需要下列能力時，就可以改用這一套：

- 簡短、以路由為主的 `AGENTS.md`
- 存放在儲存庫內、可持續維護的系統記錄文件
- 進行中與已完成的執行計畫
- 明確的產品、可靠性、安全與前端政策文件
- 依產品領域與架構層進行的品質評分
- 適合模型閱讀的參考資料目錄
- 處理架構、知識記錄與執行階段驗證的標準作業程序

## 包含的起步結構

[`repo-template/`](./repo-template/index.md) 內的起步資源包，對應下列結構：

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## 如何採用

1. 如果你的儲存庫還小，先使用最小資源包。
2. 當你需要更強的結構時，再把 [`repo-template/`](./repo-template/index.md) 內的檔案複製到自己的儲存庫。
3. 保持 `AGENTS.md` 簡短，把它當成通往較深層文件的路由，而不是百科全書。
4. 把品質、可靠性與計畫文件視為日常工作的一部分，不要留到之後集中補寫。
5. 把產生物與外部參考資料分開標示，讓代理不必依賴聊天記錄也能找到它們。

## SOP 資源庫

[`sops/`](./sops/index.md) 把文章中的圖示整理成逐步操作程序：

- 分層領域架構設定
- 把未被看見的知識編碼進儲存庫
- 本地可觀測性堆疊與回饋迴路工作流程
- 針對 UI 工作的 Chrome DevTools 驗證迴圈

## 設計原則

- 短入口，深層連結文件
- 儲存庫作為系統記錄
- 機械檢查優先於記憶規則
- 計畫與品質歷史和程式碼並列保存
- 清理與簡化是正式責任

這套資源包有明確傾向，但仍然應該依照你的專案調整，不要直接照抄。
