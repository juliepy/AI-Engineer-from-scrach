# 歡迎來到 Learn Harness Engineering

Learn Harness Engineering 是一門專注於 AI 程式設計代理工程實踐的課程。本課程深入研究並整理業界前沿的 Harness Engineering（駕馭工程）理論與實踐，參考資料包括：
- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering)

透過系統性的環境設計、狀態管理、驗證與控制機制，本課程旨在幫助你讓 Codex 和 Claude Code 等 AI 代理能夠真正可靠地完成真實工程任務。它透過明確的規則和邊界約束你的 AI 程式設計助手，幫助你更可靠地建構功能、修復 bug 並自動化開發任務。

## 開始學習

選擇適合你的學習路徑。本課程分為理論講義、實戰專案和開箱即用的資源庫。

<div class="card-grid">
  <a href="./lectures/lecture-01-why-capable-agents-still-fail/" class="card">
    <h3>講義</h3>
    <p>理解為什麼強大的模型依然會失敗，掌握建構有效 Harness 的理論基礎。</p>
  </a>
  <a href="./projects/" class="card">
    <h3>專案</h3>
    <p>動手實踐，從零開始搭建一個可靠的代理工作環境。</p>
  </a>
  <a href="./resources/" class="card">
    <h3>資源庫</h3>
    <p>開箱即用的範本（AGENTS.md、feature_list.json 等），可直接複製到你自己的儲存庫中。</p>
  </a>
</div>

## Harness 的核心機制

Harness 的核心在於為模型建立一套閉環的**工作系統**，讓模型更聰明並非其目的。你可以透過下面的簡單圖示理解它的核心運作流：

```mermaid
graph TD
    A["明確目標<br/>AGENTS.md"] --> B("初始化檢查<br/>init.sh")
    B --> C{"執行任務<br/>AI Agent"}
    C -->|遇到障礙| D["執行回饋<br/>CLI / Logs"]
    D -->|自動修復| C
    C -->|程式碼完成| E{"驗證與評審<br/>Test & QA"}
    E -->|未通過| D
    E -->|通過| F["清理與交接<br/>claude-progress.md"]
    
    classDef primary fill:#D95C41,stroke:#C14E36,color:#fff,font-weight:bold;
    classDef process fill:#F4F3EE,stroke:#D1D1D1,color:#1A1A1A;
    classDef check fill:#EAE8E1,stroke:#B3B3B3,color:#1A1A1A;
    
    class A,F primary;
    class B,D process;
    class C,E check;
```

## 你將學到什麼

你將在本課程中掌握以下核心概念：

<ul class="index-list">
  <li>用明確的規則和邊界<strong>約束代理的行為</strong>。</li>
  <li>在跨工作階段的長時任務中<strong>保持脈絡連續性</strong>。</li>
  <li><strong>防止代理提前宣告</strong>任務完成。</li>
  <li>讓代理透過完整的流水線測試及自我反思來<strong>驗證工作成果</strong>。</li>
  <li>讓代理的執行過程<strong>可觀測、可除錯</strong>。</li>
</ul>

## 下一步

了解核心概念後，可以透過以下內容深入學習：

<ul class="index-list">
  <li><a href="./lectures/lecture-01-why-capable-agents-still-fail/">L01. 模型能力強，不等於執行可靠</a>：從理論開始。</li>
  <li><a href="./projects/project-01-baseline-vs-minimal-harness/">P01. 提示詞 vs 規則驅動</a>：完成你的第一個對比實戰任務。</li>
  <li><a href="./resources/templates/">範本指南</a>：取得最小 harness 範本包（AGENTS.md、feature_list.json、claude-progress.md 等），直接用於你的專案。</li>
</ul>
