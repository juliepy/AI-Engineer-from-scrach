# middle · 压缩 prompt

> = PREAMBLE + TURNS TO SUMMARIZE(middle) + Template

- 长度: 4609 chars

---

You are a summarization agent creating a context checkpoint. Treat the conversation turns below as source material for a compact record of prior work. Produce only the structured summary; do not add a greeting, preamble, or prefix. Write the summary in the same language the user was using in the conversation — do not translate or switch to English. NEVER include API keys, tokens, passwords, secrets, credentials, or connection strings in the summary — replace any that appear with [REDACTED]. Note that the user had credentials present, but do not preserve their values.

Create a structured checkpoint summary for the conversation after earlier turns are compacted. The summary should preserve enough detail for continuity without re-reading the original turns.

TURNS TO SUMMARIZE:
user: 我是 Julie，在上海准备转 AI Agent Engineer。今天卡在 Hermes 的 `context_compressor.py`：为什么对话一长就突然「改历史」了？我以为 Prompt Cache 绝对不能动过去的 messages。
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

Extra facts to preserve (from memory provider):
用户叫 Julie；目标方向 AI Engineer（来自 on_pre_compress）

Use this exact structure:

## Historical Task Snapshot
[用户最近一条尚未完成的输入——尽量 verbatim。若用户说了 stop/undo，写反向信号且勿延续旧任务。无则写 None。]

## Goal
[用户总体想完成什么]

## Constraints & Preferences
[偏好、风格、约束、重要决定]

## Completed Actions
[编号列表：N. ACTION target — outcome [tool: name]，要具体路径/命令/结果]

## Active State
[工作目录/分支、改过的文件、测试状态、环境]

## Historical In-Progress State
[压缩触发时正在做的事]

## Blocked
[未解决的 blocker / 精确错误信息]

## Key Decisions
[技术决策 + WHY]

## Resolved Questions
[已回答的问题 + 答案，避免重复答]

## Historical Pending User Asks
[未完成的用户请求——标成 STALE，除非最新消息明确要求，否则勿执行。无则 None。]

## Relevant Files
[读过/改过/建过的文件 + 简注]

## Historical Remaining Work
[剩余工作——仅参考；非最新消息要求勿自动 resume]

## Critical Context
[否则会丢的具体值/报错/配置。密钥写 [REDACTED]]

Target ~800 tokens. Be CONCRETE — file paths, outputs, errors, line numbers.

TEMPORAL ANCHORING: The current date is 2026-07-19. When an action has already been carried out, phrase it as a completed, dated, past-tense fact rather than an open instruction.

Write only the summary body. Do not include any preamble or prefix.
