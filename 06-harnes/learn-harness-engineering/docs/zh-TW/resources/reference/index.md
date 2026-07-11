# 參考資料

這些說明用來解釋如何把範本組成一套可運作的執行環境，而不是把它們當成零散檔案。

## 內部參考說明

- [`method-map.md`](./method-map.md)：把常見的長時編碼代理失敗模式，對應到最先該補的工件或操作規則
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md)：初始化代理在功能開發開始前，應留下哪些內容
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md)：後續編碼工作固定的工作階段啟動流程
- [`prompt-calibration.md`](./prompt-calibration.md)：如何讓根指令保持明確，同時避免膨脹與僵化

## 核心文章

這份清單刻意保持狹窄。這裡的執行環境，指的是模型外部的執行系統，涵蓋代理迴圈、工具執行與沙箱，以及狀態管理、驗證與可觀測性。一般性的提示工程或寬泛的代理框架文章，不放進核心清單。

原始的三篇文章仍是課程骨幹：

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)（2026-02-11）：代理優先的儲存庫、儲存庫在地脈絡、自訂 lint 與結構護欄。
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（2025-11-26）：初始化代理、編碼代理、功能清單、進度日誌，以及跨上下文視窗的交接。
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026-03-24）：planner / generator / evaluator 角色、上下文重設、執行環境簡化與過時假設。

另外只加入少數高度相關的 2026 文章：

- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)（2026-01-23）：Codex 執行期執行環境、工具呼叫、脈絡增長與迴圈終止。
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)（2026-01-09）：把模型與執行環境一起評估，並區分 evaluation harness 與 agent harness。
- [LangChain: Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)（2026-02-17）：在模型不變的情況下，調整 system prompt、tools、middleware、tracing 與自我驗證，讓編碼代理在 Terminal Bench 2.0 從 Top 30 提升到 Top 5。
- [Thoughtworks / Martin Fowler: Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)（2026-04-02）：把編碼代理使用者的執行環境拆成 feedforward guides 與 feedback sensors，並區分 deterministic controls 與 inferential controls。
- [Cursor: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)（2026-04-30）：把執行環境視為持續改進的產品系統，透過離線評估、線上 metrics、工具錯誤分類、模型調校與 mid-chat model switching 改善行為。

## 2026 延伸參考

這些不是課程核心來源，但在設計特定執行環境模組時仍有價值。這一節只保留正文直接討論代理迴圈、工具執行與脈絡管理，或深入分析驗證、沙箱與治理機制的來源。純產品介紹、平臺公告、團隊案例與 benchmark 文章不放在這裡。

- [OpenAI: Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/)（2026-02-04）：把執行環境抽象成可重用的 App Server 協定，涵蓋 thread lifecycle、resume、fork、diff 與客戶端整合。
- [OpenAI Developers: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)（2026-02-23）：長時任務中的持久專案記憶、里程碑驗證與 done-when 範例。
- [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)（2026-04-15）：模型原生的執行環境、沙箱執行與檔案／命令執行能力。
- [OpenAI: An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)（2026-04-27）：把 issue tracker 或 Linear 看板轉成多代理控制平面。
- [Anthropic: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)（2026-02-05）：平行代理團隊、任務鎖、git 同步、容器隔離與自主迴圈。
- [Anthropic: Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)（2026-04-08）：從 meta-harness 角度，把工作階段、執行環境與沙箱拆成可替換介面。
- [Anthropic: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)（2026-04-23）：reasoning effort、脈絡裁剪與 system prompt 都屬於執行環境變更，且需要迴歸治理。
- [LangChain: Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents)（2026-01-28）：以 filesystem offloading、tool-call truncation、summarization 與 targeted evals 建構脈絡管理執行環境。
- [LangChain: Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models)（2026-04-29）：針對不同模型，以提示詞、工具名稱、middleware 與子代理設定建立專屬執行環境設定檔。
- [LangChain: Continual learning for AI agents](https://www.langchain.com/blog/continual-learning-for-ai-agents)（2026-04-05）：把代理改進拆成模型、執行環境與脈絡三層，並以 traces 作為改進訊號。
- [Microsoft: Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/)（2026-03-12）：shell／filesystem 執行環境、核准流程、託管 shell 執行與脈絡壓縮。
- [Google: Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/)（2026-03-30）：plugins、event compaction、HITL、session／memory services 與 A2A，可作為可重用的執行環境原語。
- [GitHub: Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)（2026-02-13）：把 GitHub Actions 當成代理式工作流程執行器，涵蓋 safe outputs、sandboxing、permissions 與 review。
- [AWS: AI agents in enterprises: Best practices with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/)（2026-02-03）：企業執行環境分層，包括 Runtime、Memory、Gateway、Identity／Policy、Observability 與 Evaluations。
- [Stripe: Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)（2026-02-09）與 [Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)（2026-02-19）：devbox 隔離、自訂代理執行環境、blueprint 狀態機、規則檔案、MCP tool curation、安全控制與 pre-push／CI 回饋迴圈。
- [Cognition: What We Learned Building Cloud Agents](https://cognition.ai/blog/what-we-learned-building-cloud-agents)（2026-04-23）：雲端代理執行期的 VM 隔離、工作階段快照／恢復、協調、治理、稽核日誌與整合。
- [Cognition: Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)（2026-04-22）：generator-verifier 迴圈、乾淨脈絡 reviewer、smart-friend routing、manager-child coordination 與跨代理通訊邊界。
- [Replit: Decision-Time Guidance: Keeping Replit Agent Reliable](https://blog.replit.com/decision-time-guidance)（2026-01-20，2026-01-23 更新）：在決策點以輕量分類器注入短指令，而不是把所有規則塞進系統提示詞。
- [Vercel: How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent)（2026-01-07）：動態系統提示詞、串流重寫層與 deterministic／model-driven 自動修復器。
- [Vercel: Introducing deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base)（2026-05-04）：面向安全掃描的編碼代理執行環境，包含 scan、investigate、revalidate、enrich、export、plugin 與 refusal-checker 步驟。
- [Sourcegraph: CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks)（2026-03-03）：可作為 eval／tooling 執行環境參考，涵蓋 MCP tool 採用、tool-use transcripts、benchmark QA、verifier／reproducibility gates 與 prompt／preamble 迭代。

嚴格來說，只屬於 2025 的一般參考資料不會進入核心清單。原始的 Anthropic 2025 文章仍保留，因為它是本課程的方法基礎。

## 建議閱讀順序

1. `method-map.md`
2. `initializer-agent-playbook.md`
3. `coding-agent-startup-flow.md`
4. `prompt-calibration.md`
5. OpenAI Harness engineering
6. Anthropic Effective harnesses
7. Anthropic Harness design for long-running application development
8. OpenAI Codex agent loop
9. Anthropic agent evals
10. LangChain Improving Deep Agents
11. Thoughtworks / Martin Fowler Harness engineering for coding agent users
12. Cursor Continually improving our agent harness
