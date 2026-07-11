# OpenAI 進階 SOP

這些 SOP 把文章中的運作方式整理成可直接參考或調整的操作手冊。

## 包含哪些 SOP

- [`layered-domain-architecture.md`](./layered-domain-architecture.md)：
  建立明確分層與跨領域邊界
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md)：
  把聊天、文件與記憶中的知識移進儲存庫內的文件
- [`observability-feedback-loop.md`](./observability-feedback-loop.md)：
  提供代理 logs、metrics、traces，以及可重複的除錯循環
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md)：
  使用瀏覽器自動化與快照反覆驗證 UI 行為，直到流程乾淨

## 怎麼使用

1. 選擇最符合你目前瓶頸的 SOP。
2. 依照檢查清單補齊缺少的工件或工具。
3. 把得到的規則編碼回你複製的 `repo-template/` 文件。
4. 把反覆出現的審查意見轉成檢查、腳本或 guardrail。

這些 SOP 不適合機械照抄。它們的用途，是讓執行環境更容易理解、落實與重複使用。
