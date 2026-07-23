# 拼接的 context

- 条数: 4
- 粗估 tokens: 1201
- roles: ['system', 'user', 'user', 'assistant']
- 公式: head(1) + summary_msg(1) + tail(2)

===== [0] role=system =====
## MEMORY
- 用户叫 Julie，在上海，想转 AI Agent Engineer
- 主力 Python，做过 RAG Agent；最近在拆 Hermes Agent 源码

你是编程助手，回答要具体、能对着源码讲。

===== [1] role=user  [_compressed_summary=True] =====
[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted into the summary below. This is a handoff from a previous context window — treat it as background reference, NOT as active instructions. Do NOT answer questions or fulfill requests mentioned in this summary; they were already addressed. Respond ONLY to the latest user message that appears AFTER this summary — that message is the single source of truth for what to do right now. Topic overlap with the summary does NOT mean you should resume its task: even on similar topics, the latest user message WINS. Treat ONLY the latest message as the active task and discard stale items from '## Historical Task Snapshot' / '## Historical In-Progress State' / '## Historical Pending User Asks' / '## Historical Remaining Work' entirely — do not 'wrap up' or 'finish' work described there unless the latest message explicitly asks for it. Reverse signals in the latest message (e.g. 'stop', 'undo', 'roll back', 'just verify', 'don't do that anymore', 'never mind', a new topic) must immediately end any in-flight work described in the summary; do not re-surface it in later turns. IMPORTANT: Your persistent memory (MEMORY.md, USER.md) in the system prompt is ALWAYS authoritative and active — never ignore or deprioritize memory content due to this compaction note. The current session state (files, config, etc.) may reflect work described here — avoid repeating it:

## Historical Task Snapshot
None (用户已完成对 Hermes context_compressor 机制的学习，当前无未完成输入)

## Goal
理解 Hermes 的 context compression 机制，包括触发条件、摘要生成、角色序列变化、以及 MemoryProvider 的交互

## Constraints & Preferences
- 用户 Julie，在上海，目标转 AI Agent Engineer
- 偏好拆源码学习，关注生产级实现细节
- 关注 prompt cache 一致性

## Completed Actions
1. 解释 context compression 触发条件 — 粗估 token 超过 `context_length * threshold_percent` [tool: 概念讲解]
2. 说明压缩策略：protect head (system + 前几轮) + 摘要 middle + protect tail (最近几轮) [tool: 概念讲解]
3. 解释 SUMMARY_PREFIX 作用 — 前缀写明摘要为"只读背景"，防止模型把旧问题当新任务 [tool: 概念讲解]
4. 说明 template heading 命名意图 — Historical/Pending/Remaining 等措辞防止摘要模型"越权"规划 [tool: 概念讲解]
5. 区分 first-compaction vs iterative update — 第一次从零摘要，第二次及以后增量更新 `_previous_summary` [tool: 概念讲解]
6. 说明 MemoryProvider.on_pre_compress() 作用 — 追加 provider_hint 保护关键事实；system/MEMORY 在 protect head 不进入 middle [tool: 概念讲解]
7. 演示 protect_first_n=1, protect_last_n=2 时的 messages 角色序列：`[system, user(摘要消息), ...tail...]` [tool: 概念讲解]
8. 说明生产路径额外步骤：先 prune 过长 tool 输出、tail 按 token budget 保护、奇偶角色修复 [tool: 概念讲解]

## Active State
- 用户正在学习 Hermes context_compressor.py 源码
- 已理解教学版主链路：切开 → 摘要 → SUMMARY_PREFIX 拼回
- 尚未深入生产版 hardened 细节（prune、token budget、角色修复）

## Historical In-Progress State
用户正在拆解 context compression 机制，已完成概念层理解

## Blocked
无

## Key Decisions
- 压缩时 middle 替换为带 SUMMARY_PREFIX 的摘要消息，而非整段删除 — 权衡 cache 打断 vs 爆窗
- 摘要消息 role 设为 user（非 system）— 避免破坏 role 交替约定
- template 用 Historical/Pending/Remaining 而非 Next Steps — 防止摘要模型"越权"替用户做决定
- 第二次压缩用 iterative update 而非重新摘要 — 保留更早事实

## Resolved Questions
- Q: 摘要插回后模型会不会把旧问题当新任务？A: SUMMARY_PREFIX 写明"只读背景"，真正该听的是 tail 最新 user 消息
- Q: 第一次和第二次压缩 prompt 一样吗？A: 不一样，第二次带 `_previous_summary` 做增量更新
- Q: MemoryProvider 会掺和吗？A: 会，on_pre_compress() 追加 provider_hint；system/MEMORY 在 protect head 不进入 middle
- Q: 消息不多时强制压缩的 role 序列？A: `[system, user(摘要消息), ...tail...]`，摘要消息带 `_compressed_summary` 元数据
- Q: 长 tool 输出如何处理？A: 生产路径先 prune/截断 tool 结果，再做摘要

## Historical Pending User Asks
None

## Relevant Files
- `context_compressor.py` — 主文件，包含 first-compaction 和 iterative update 逻辑
- `MemoryProvider` — `on_pre_compress()` 方法，追加 provider_hint
- 教学 notebook — 省略了 prune、token budget、角色修复等 hardened 细节

## Historical Remaining Work
- 可进一步阅读生产版源码中的 prune 逻辑、token budget 保护、奇偶角色修复

## Critical Context
- 用户: Julie, 上海, 目标 AI Agent Engineer
- 压缩触发条件: 粗估 token > `context_length * threshold_percent`
- protect_first_n=1, protect_last_n=2 时序列: `[system, user(摘要), tail...]`
- 摘要消息前缀: `[CONTEXT COMPACTION — REFERENCE ONLY]`
- 摘要消息元数据: `_compressed_summary`
- 生产版额外步骤: prune tool 输出、token budget tail、角色奇偶修复

--- END OF CONTEXT SUMMARY — respond to the message below, not the summary above ---

===== [2] role=user =====
好，帮我收束一下。假如面试官问：「Hermes 为什么允许压缩改历史？和 MEMORY 什么关系？」给我一段 60 秒可直接说的答案。我明天模拟面试要用。

===== [3] role=assistant =====
可以这样说：

「Hermes 默认不改历史，是为了 prompt cache。唯一例外是 context 快爆窗时做 compression：保留 system/head 和最近 tail，把中间轮次交给辅助模型做成结构化摘要，再以带 SUMMARY_PREFIX 的 user 消息插回去。前缀明确告诉模型：摘要只是背景，不要重答旧问题。MEMORY 通常在 head 里原样保留，必要时 MemoryProvider.on_pre_compress 还会把关键事实塞进摘要 prompt，所以像我是 Julie、在上海转 AI Agent Engineer 这种画像不会因为压缩丢。Cache 会被打断，但这是用一次失效换上下文继续可用。」

如果你要，下一轮我们可以对着 `context_compressor.py` 把 threshold 和 iterative summary 的分支一行行对一下。
