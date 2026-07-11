# 中文参考

这一部分解释这些模板该怎么配合使用，而不是把它们当成一堆孤立文件。

## 内部参考材料

- [`method-map.md`](./method-map.md)：把常见长时任务翻车点映射到对应方法和工件
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md)：初始化代理在第一轮应该产出什么
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md)：后续编码代理每次开工的固定流程
- [`prompt-calibration.md`](./prompt-calibration.md)：根指令应该写到什么程度才合适

## 重点参考文章

这里的筛选标准很窄：只保留能直接解释 harness 机制的文章。Harness 在这里指模型外部的运行系统，包括 agent loop、工具执行、沙箱、状态、上下文、验证、终止条件、控制平面和观测反馈；不是泛泛的 prompt engineering 或 agent 框架介绍。

保留原始三篇作为课程主轴：

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)（2026-02-11）：agent-first 仓库、repo-local context、custom lint、结构性 guardrail。
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（2025-11-26）：initializer agent、coding agent、feature list、progress log、跨上下文窗口交接。
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026-03-24）：planner / generator / evaluator 三角色、context reset、harness 简化和组件过期问题。

额外只加入几篇高相关、高含金量的 2026 文章：

- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)（2026-01-23）：解释 Codex runtime harness 的核心循环、工具调用、上下文增长和终止状态。
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)（2026-01-09）：明确评估 agent 时评的是 model + harness，并区分 evaluation harness 与 agent harness。
- [LangChain: Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)（2026-02-17）：同一模型不变，只改 system prompt、tools、middleware、tracing 和 self-verification，让 coding agent 在 Terminal Bench 2.0 上从 Top 30 进到 Top 5。
- [Thoughtworks / Martin Fowler: Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)（2026-04-02）：把 coding-agent user harness 拆成 feedforward guides 和 feedback sensors，并区分 deterministic controls 与 inferential controls。
- [Cursor: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness)（2026-04-30）：把 harness 当成持续迭代的产品系统，用离线评估、线上指标、工具错误分类、模型定制和 mid-chat model switching 改善 agent 行为。

## 2026 扩展参考

这些文章不作为课程主轴，但在设计特定 harness 模块时很有借鉴价值。只保留文章正文直接涉及 agent loop、工具执行、上下文管理、验证、沙箱、控制层、回归治理等机制的材料；纯 agent 产品、平台发布、团队实践或 benchmark 不放进这里。

- [OpenAI: Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/)（2026-02-04）：把 harness 抽象成 App Server 协议，覆盖 thread lifecycle、resume、fork、diff 和客户端集成。
- [OpenAI Developers: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)（2026-02-23）：长时任务中的 durable project memory、milestone validation 和 done-when 例子。
- [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)（2026-04-15）：model-native harness、sandbox execution、文件与命令执行能力。
- [OpenAI: An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)（2026-04-27）：把 issue tracker / Linear 变成多 agent 控制平面。
- [Anthropic: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)（2026-02-05）：并行 agent 团队、任务锁、git 同步、容器隔离和自主循环。
- [Anthropic: Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)（2026-04-08）：meta-harness 视角，把 session、harness、sandbox 拆成可替换接口。
- [Anthropic: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)（2026-04-23）：reasoning effort、context pruning、system prompt 都属于 harness 变更，且需要回归治理。
- [LangChain: Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents)（2026-01-28）：filesystem offloading、tool-call truncation、summarization 和 targeted evals 组成的 context-management harness。
- [LangChain: Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models)（2026-04-29）：用 model-specific harness profiles 调整 prompt、tool names、middleware 和 subagent 配置。
- [LangChain: Continual learning for AI agents](https://www.langchain.com/blog/continual-learning-for-ai-agents)（2026-04-05）：把 agent 改进拆成 model、harness、context 三层，并把 traces 作为改进信号。
- [Microsoft: Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/)（2026-03-12）：shell/filesystem harness、approval flow、hosted shell、context compaction。
- [Google: Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/)（2026-03-30）：插件、event compaction、HITL、session/memory service、A2A 等可复用 harness primitives。
- [GitHub: Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)（2026-02-13）：把 GitHub Actions 变成 agentic workflow runner，包含 safe outputs、sandboxing、permissions、review。
- [AWS: AI agents in enterprises: Best practices with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/)（2026-02-03）：Runtime、Memory、Gateway、Identity/Policy、Observability、Evaluations 的企业级 harness 分层。
- [Stripe: Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)（2026-02-09）和 [Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)（2026-02-19）：devbox 隔离、custom agent harness、blueprints 状态机、规则文件、MCP tool curation、安全控制、pre-push/CI 反馈循环。
- [Cognition: What We Learned Building Cloud Agents](https://cognition.ai/blog/what-we-learned-building-cloud-agents)（2026-04-23）：云端 agent runtime 的 VM 隔离、session snapshot/resume、orchestration、governance、audit logging 和 integrations。
- [Cognition: Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)（2026-04-22）：generator-verifier loop、clean-context reviewer、smart-friend routing、manager-child coordination 和跨 agent 通信边界。
- [Replit: Decision-Time Guidance: Keeping Replit Agent Reliable](https://blog.replit.com/decision-time-guidance)（2026-01-20，2026-01-23 更新）：用轻量分类器在关键决策点注入短指令，而不是把所有规则塞进系统提示词。
- [Vercel: How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent)（2026-01-07）：动态系统提示、streaming rewrite layer 和 deterministic/model-driven autofixers。
- [Vercel: Introducing deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base)（2026-05-04）：面向安全扫描的 coding-agent harness，包含 scan、investigate、revalidate、enrich、export、plugin 和 refusal-checker。
- [Sourcegraph: CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks)（2026-03-03）：偏 eval/tooling harness，包含 MCP tool adoption、tool-use transcripts、benchmark QA、verifier/reproducibility gates 和 prompt/preamble 迭代。

严格按时间筛选时，2025-only 的泛参考不进入主列表。原始三篇中的 Anthropic 2025 文章保留，是因为它是本课程方法的基础来源。

## 推荐阅读顺序

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
