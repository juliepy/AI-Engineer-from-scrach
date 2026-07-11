# 範例：將審查回饋轉化為規則

重複的審查意見：

> 不要從 renderer 呼叫檔案系統工具。使用 preload 橋樑。

提升為 harness 規則：

- 新增 lint 或匯入規則以防止在 renderer 程式碼中使用 `fs`
- 新增修復說明文字，解釋 preload 邊界
