## Historical Task Snapshot
用户请求：“好，帮我收束一下。假如面试官问：「Hermes 为什么允许压缩改历史？和 MEMORY 什么关系？」给我一段 60 秒可直接说的答案。我明天模拟面试要用。”  
该请求尚未被满足；助理尚未生成这段面试话术。

## Goal
Julie 正在准备 TUV（仪器仪表检测认证公司）AI 工程师线下二面，希望通过深入理解 Hermes 上下文压缩的内部机制，形成可直接用于面试的结构化回答，并掌握“为什么这么设计”的面试话术。整体目标是为 AI + 仪器仪表测试自动化岗位积累技术深度。

## Constraints & Preferences
- 语言：中文交流，技术术语可保留英文。
- 回答风格：严谨导师型，需包含“面试官意图→标准回答→深层解析→加分点→关联项目”的结构。
- 组织方式：偏好分场景整理（已创建 TUV_二面场景准备.md）。
- 职业方向：只聚焦 AI Agent Engineer / RAG Engineer 等纯开发岗，不投 PM。Julie 具有 Python 主力 + C 背景，持有 CCIE 安全认证，做过 RAG Agent 项目。
- 面试后会将答不出来的问题带回讨论，需要面试话术级别的答案。

## Completed Actions
1. 解释 Hermes 压缩触发条件：粗估 token 越过 `context_length * threshold_percent` 时触发，protect head（含 system + MEMORY）、middle 序列化摘要、protect tail。
2. 说明 `SUMMARY_PREFIX` 的作用：摘要消息会以特定前缀 + END marker 插入，明确声明为“只读背景”，防止模型把前情提要当成当前任务重新回答。
3. 解释摘要模板措辞（Historical Task、Pending Asks、Remaining Work 等）的设计意图：用历史归档语言而非 actionable 语言，防止摘要模型越权替用户做决策。
4. 说明首次压缩与后续压缩的差异：首次走 first‑compaction，第二次及以后走 iterative update，会携带上 `_previous_summary` 增量更新，避免丢失更早 key facts。
5. 解释 MemoryProvider 的参与方式：`on_pre_compress()` 在压缩前将“别丢的事实”作为 `provider_hint` 追加进提示，优先靠 head + memory 保住，补充摘要模型的不可靠性。
6. 给出强制压缩后的消息顺序示例（protect_first_n=1, protect_last_n=2）：`[system, user(摘要消息), …tail最后两条]`，注意摘要消息的 role 为 user，通过 metadata 识别。
7. 补充真实源码中更激进的优化：prune/token budget、尾窗动态保护、奇偶角色修复等，并指出教学 notebook 仅为展示主链路。

## Active State
- 当前无实际文件编辑；工作在对话上下文展开。
- Julie 明天将进行模拟面试，需要一段可直接使用的 60 秒回答。

## Historical In‑Progress State
助理正在为 Julie 组装关于“Hermes 为何允许压缩改历史以及与 MEMORY 关系”的面试话术。

## Blocked
无阻塞项；等待助理产出该回答。

## Key Decisions
- 摘要采用 `SUMMARY_PREFIX` 而非裸文本，是防止摘要成为新指令的关键设计。
- 模板避免使用“Next Steps”等措辞，通过 Historical/Pending/Remaining 让摘要模型保持归档心态。
- 迭代压缩必须保留上一份 summary，避免信息逐次衰减。
- 背景信息（如 Julie 的身份、转岗目标）应优先通过 head 保护和 provider_hint 留存，而非依赖摘要模型的偶然记忆。

## Resolved Questions
- 摘要插回后是否会重复回答旧问题？不会，因为有 `SUMMARY_PREFIX` 标注为只读背景。
- 模板中奇怪的 heading 是设计吗？是，且有意为之，以防止摘要模型越权。
- 第二次压缩会不会丢失第一次的摘要？不会，迭代压缩会基于旧摘要更新。
- MemoryProvider 在压缩中会被忽略吗？不会，且通过 hint 和头部保护双保险。
- 本地复现压缩后的消息 role 序列是什么样的？`[system, user(摘要), …tail]`，具体结构已给出。
- 源码中是否会对 tool 输出做额外处理？会，真实实现常包含 prune、token budget 和角色修复。

## Historical Pending User Asks
无（所有历史问题均已解答）。

## Relevant Files
- 教学 notebook：展示压缩主链路，省略了 prune 等 hardened 细节。
- 内部模块：`context_compressor`（压缩引擎）、`MemoryProvider`（记忆提供器）。
- 用户文件：`TUV_二面场景准备.md`（面试准备文档）。

## Historical Remaining Work
无。

## Critical Context
- 用户身份：Julie，软件工程师，常住上海，Python 主力 + C 背景，持有 CCIE 安全，有过 RAG Agent 项目。正寻找 AI Agent Engineer 岗位，已通过 TUV 一面，在准备线下二面（AI + 仪器仪表测试自动化）。
- 关键压缩原则：压缩是对 middle 窗口的归档摘要，不是新指令；`SUMMARY_PREFIX` 保证摘要仅为背景；head 中的 system/MEMORY 一般不会被移入摘要，而是保留原样。
- 面试话术要求：能够清晰解释 Hermes 允许压缩改历史的原因是“权衡窗口爆掉和 cache 中断”，且压缩始终保留关键背景并通过 memory 稳定传承。