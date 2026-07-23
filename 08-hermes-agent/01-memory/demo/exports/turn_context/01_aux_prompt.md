You are a summarization agent creating a context checkpoint. Treat the conversation turns below as source material for a compact record of prior work. Produce only the structured summary; do not add a greeting, preamble, or prefix. Write the summary in the same language the user was using in the conversation — do not translate or switch to English. NEVER include API keys, tokens, passwords, secrets, credentials, or connection strings in the summary — replace any that appear with [REDACTED]. Note that the user had credentials present, but do not preserve their values.

Create a structured checkpoint summary for the conversation after earlier turns are compacted. The summary should preserve enough detail for continuity without re-reading the original turns.

TURNS TO SUMMARIZE:
assistant: Julie，你的直觉大体对：Hermes 平时确实不改历史，为的是保住 per-conversation 的 prompt cache。

唯一例外就是 context compression。触发条件大致是：当前 messages 的粗估 token 越过 `context_length * threshold_percent`。一旦触发，不会整段删掉，而是切开：

1. **protect head**：通常保住 system（含你 MEMORY 里「Julie / 上海 / AI Engineer」）和前几轮
2. **middle**：中间轮次序列化成文本，丢给辅助模型做结构化摘要
3. **protect tail**：最近几轮原样留下，因为还在接着干

所以「改历史」不是乱改，而是把 middle 换成一条带 `SUMMARY_PREFIX` 的摘要消息。Cache 会被这一刀打断——这是刻意权衡：爆窗比多花一点 cache 更糟。
user: 那摘要插回去之后，模型会不会把摘要里的旧问题又答一遍？我怕它把「前情提要」当成当前任务。
assistant: 这就是 `SUMMARY_PREFIX` 存在的原因。拼回 messages 时不是裸摘要，而是：

`SUMMARY_PREFIX` + 结构化摘要正文 + `END` marker

前缀里会写明：这是上一窗口的 handoff，只作背景参考，**不要**去回答摘要里提到的旧问题。真正该听的是 tail 里最新的 user 消息。

面试话术可以记一句：压缩后的摘要是「只读背景」，不是「新指令」。
user: template 里那些 heading 好奇怪：Historical Task、Pending Asks、Remaining Work……为什么不直接写 Next Steps？我看着像项目管理模板。
assistant: 命名是有意的。摘要模型很容易「越权」：看到 Next Steps 就开始规划、甚至替用户做决定。

Hermes 用 Historical / Pending / Remaining 这类措辞，是在告诉 summarizer：你在归档**已经发生过的对话**，不是在开新 sprint。Completed Actions、Critical Context 也是为了把「做过什么 / 别丢的事实」压出来，方便下一窗口接着聊。

对你这种拆源码学习很有用：压缩后仍应留下「Julie、上海、AI Engineer、正在看 context_compressor」这类 Critical Context。
user: 第一次压缩和第二次压缩，prompt 一样吗？我担心第二次会把第一次的摘要弄丢。
assistant: 不一样。第一次走 first-compaction：从零摘要 middle。

第二次及以后走 iterative update：会把 `_previous_summary` 带进 prompt，让辅助模型在旧摘要上增量更新，而不是把更早的事实整段忘掉。这也是为什么 compressor 实例会缓存上一份 summary。

实操含义：长会话连压两次时，Julie 的身份信息和已讲过的压缩机制要点，更可能留在 Critical Context 里，而不是只剩最后两轮闲聊。
user: MemoryProvider 的 `on_pre_compress` 会掺和进来吗？我 MEMORY.md 里写了转岗目标，压缩时会不会被摘要模型忽略？
assistant: 会掺和，而且是加分项。压缩前可以走 `MemoryProvider.on_pre_compress()`，把「别丢的事实」追加进送给 summarizer 的文本（教学版里叫 `provider_hint`）。

另外两道保险：

1. system / MEMORY 通常在 protect head，根本不进 middle
2. `SUMMARY_PREFIX` 明文提醒：别因为压缩就忽略 memory

所以转岗目标「AI Agent Engineer」这类稳定画像，优先靠 head + provider hint 保住，而不是赌摘要模型自己记得。
user: 我本地想复现：消息不太多时强制压缩，protect_first_n=1、protect_last_n=2，最后 messages 的 role 序列大概长什么样？
assistant: 典型形态是：

`[system, user(摘要消息), …tail…]`

你设 protect_first_n=1、protect_last_n=2 时，大致是：

- `[0]` system（head）
- `[1]` user —— 内容以 `[CONTEXT COMPACTION — REFERENCE ONLY]` 开头，并带 `_compressed_summary` 元数据
- 最后两条 = 压缩前最后一轮 user + assistant（tail）

注意：摘要那条的 role 是 **user**（不是 system），避免破坏后面的 role 交替约定；前端识别靠 metadata / 前缀，上线前 wire 会剥掉 `_` 开头的内部 key。
user: 还有个细节：middle 里如果有很长的 tool 输出，真源码是不是先砍 tool，再做摘要？我在 PR 讨论里好像看到过 prune。
assistant: 对，生产路径比教学版更凶一点。真 `ContextCompressor` 往往还会：

- 先对过长的 tool 结果做 prune / 截断
- tail 按 **token budget** 保护，而不是死板固定 N 条
- 处理合并进 tail 后的奇偶角色修复，避免出现两个同 role 连在一起

教学 notebook 把这些省略了，只保留「切开 → 摘要 → SUMMARY_PREFIX 拼回」主链路，方便你先把 cache 例外讲清楚，再去看源码里的 hardened 细节。
user: 好，帮我收束一下。假如面试官问：「Hermes 为什么允许压缩改历史？和 MEMORY 什么关系？」给我一段 60 秒可直接说的答案。我明天模拟面试要用。

Extra facts to preserve (from memory provider):
USER.md facts:
Julie，软件工程师，正在找 AI Agent Engineer 工作。Python 主力 + C 背景。持有 CCIE 安全认证。做过 RAG Agent 项目。目前二面通过 TUV（仪器仪表检测认证公司），正在准备线下二面，岗位方向是 AI + 仪器仪表测试自动化。面试后会把答不出来的问题带回来讨论，偏好结构化、分场景的面试准备方式。中文交流，技术术语英文可保留。

MEMORY.md facts:
Julie 偏好严谨导师型面试辅导，标准回答结构：面试官考察意图 → 标准回答 → 深层解析 → 加分点 → 关联她的项目经验。喜欢分场景整理（写了 TUV_二面场景准备.md）。面试遇到不会的问题会带回来深挖，需要面试话术级别的回答。
Julie 面了中通 AI Product Manager 挂了，发现自己不适合 PM 方向，更喜欢也擅长开发。应聚焦 AI Agent Engineer / RAG Engineer 等纯开发岗，不投 PM。目前 TUV 仪器仪表 AI 工程师已过一面，在准备二面（线下）。

Use this exact structure:

## Historical Task Snapshot
[THE SINGLE MOST IMPORTANT FIELD. Capture the user's most recent unfulfilled
input verbatim — the exact words they used. This includes:
- Explicit task assignments ("refactor the auth module")
- Questions awaiting an answer ("waarom staat X op Y?", "wat zijn de volgende stappen?")
- Decisions awaiting input ("optie A of B?")
- Ongoing discussions where the assistant owes the next substantive reply
A conversation where the user just asked a question IS an active task — the
task is "answer that question with full context". Do NOT write "None" merely
because the user did not issue an imperative command; reserve "None" for the
rare case where the last exchange was fully resolved and the user said
something like "thanks, that's all".
If multiple items are outstanding, list only the ones NOT yet completed.
Continuation should pick up exactly here. Examples:
"User asked: 'Now refactor the auth module to use JWT instead of sessions'"
"User asked: 'Waarom stond provider ineens op openrouter?' — needs investigation + answer"
"User chose option A; awaiting implementation of step 2"
If the user's most recent message was a reverse signal (stop, undo, roll
back, never mind, just verify, change of topic) that supersedes earlier
work, write the reverse signal verbatim and DO NOT carry forward the
cancelled task. Example: "User asked: 'Stop the i18n refactor and just
verify the current diff' — earlier i18n in-flight work is cancelled."
If no outstanding task exists, write "None."]

## Goal
[What the user is trying to accomplish overall]

## Constraints & Preferences
[User preferences, coding style, constraints, important decisions]

## Completed Actions
[Numbered list of concrete actions taken — include tool used, target, and outcome.
Format each as: N. ACTION target — outcome [tool: name]
Example:
1. READ config.py:45 — found `==` should be `!=` [tool: read_file]
2. PATCH config.py:45 — changed `==` to `!=` [tool: patch]
3. TEST `pytest tests/` — 3/50 failed: test_parse, test_validate, test_edge [tool: terminal]
Be specific with file paths, commands, line numbers, and results.]

## Active State
[Current working state — include:
- Working directory and branch (if applicable)
- Modified/created files with brief note on each
- Test status (X/Y passing)
- Any running processes or servers
- Environment details that matter]

## Historical In-Progress State
[Work currently underway — what was being done when compaction fired]

## Blocked
[Any blockers, errors, or issues not yet resolved. Include exact error messages.]

## Key Decisions
[Important technical decisions and WHY they were made]

## Resolved Questions
[Questions the user asked that were ALREADY answered — include the answer so it is not repeated]

## Historical Pending User Asks
[Questions or requests from the user that have NOT yet been answered or fulfilled. These are STALE — they were from the compacted turns. Write them here for reference only. The agent must NOT act on them unless the latest user message explicitly requests it. If none, write "None."]

## Relevant Files
[Files read, modified, or created — with brief note on each]

## Historical Remaining Work
[What remains to be done — framed as STALE context for reference only. The agent must NOT resume this work unless the latest user message explicitly asks for it.]

## Critical Context
[Any specific values, error messages, configuration details, or data that would be lost without explicit preservation. NEVER include API keys, tokens, passwords, or credentials — write [REDACTED] instead.]

Target ~800 tokens. Be CONCRETE — include file paths, command outputs, error messages, line numbers, and specific values. Avoid vague descriptions like "made some changes" — say exactly what changed.

TEMPORAL ANCHORING: The current date is 2026-07-22. When an action has already been carried out, phrase it as a completed, dated, past-tense fact rather than an open instruction. For example, rewrite "email John about the proposal" as "Sent the proposal email to John on 2026-07-22." Never leave a finished action worded as if it still needs doing, and never invent a date for work that has not happened yet.

Write only the summary body. Do not include any preamble or prefix.