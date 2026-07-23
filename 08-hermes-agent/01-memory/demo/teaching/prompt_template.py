# =============================================================================
# 压缩摘要 Prompt 模板（对照 hermes_src/agent/context_compressor.py）
# =============================================================================
# 源码原文拷贝：heading / SUMMARY_PREFIX / _generate_summary() 积木。
# 勿缩写字符串；与真源码保持一致便于对照讲解。
#
# 两条消费路径（讲解时务必分清）：
#   1) 辅助模型（summarizer）：吃 SUMMARIZER_PREAMBLE + 首压/迭代指令
#      + _template_sections → 产出结构化摘要正文
#   2) 主模型（main chat）：吃 SUMMARY_PREFIX + 摘要正文 + SUMMARY_END_MARKER
#      作为一条 user 消息插回 history，再跟最新 user 一起发给主模型
# =============================================================================
from __future__ import annotations

# =============================================================================
# A. 结构化摘要 section headings
# -----------------------------------------------------------------------------
# 这些 heading 同时出现在：
#   - 辅助模型的「输出骨架」(_template_sections) —— 要求摘要按这些 section 写
#   - 主模型的 SUMMARY_PREFIX —— 点名这些 section 是 STALE，禁止续做
# 用常量而不是字面量，避免两边字符串漂移。
# =============================================================================

# 当前未完成的「活跃任务」快照（用户最近一句未兑现输入）。
# 辅助模型必须尽量 verbatim 抄用户原话；主模型则被告知：这里是历史，不是当前指令。
HISTORICAL_TASK_HEADING = "## Historical Task Snapshot"

# 压缩触发时仍在进行中的工作（工具调用半截、改文件中途等）。
# 标记 Historical，防止主模型把「正在做」误当成「现在继续做」。
HISTORICAL_IN_PROGRESS_HEADING = "## Historical In-Progress State"

# 压缩窗口里用户问过但还没答的问题 —— STALE。
# 主模型默认禁止主动回答；除非最新 user 消息明确要求。
HISTORICAL_PENDING_ASKS_HEADING = "## Historical Pending User Asks"

# 压缩前还没做完的剩余工作清单 —— 同样 STALE，仅作参考。
HISTORICAL_REMAINING_WORK_HEADING = "## Historical Remaining Work"

# =============================================================================
# B. 插回主模型 messages 的摘要包装（主模型侧护栏）
# -----------------------------------------------------------------------------
# compress() 拼装：
#   role=user
#   content = SUMMARY_PREFIX + "\n\n" + summary + "\n\n" + SUMMARY_END_MARKER
# 这条消息夹在 protect_first_n（head）和 protect_last_n（tail）之间。
# =============================================================================

# 摘要正文之前的长护栏。核心意图（面试常问）：
#   1. 摘要 = REFERENCE ONLY，不是 active instructions
#   2. 只响应摘要之后的最新 user message
#   3. 即使话题重叠，也以最新消息为准（latest WINS）
#   4. 上面四个 Historical section 一律视为过期，禁止「收尾/续做」
#   5. stop/undo/never mind 等反向信号必须立刻终止摘要里的在途工作
#   6. system 里的 MEMORY.md / USER.md 永远权威，压缩不得覆盖
SUMMARY_PREFIX = (
    "[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted "
    "into the summary below. This is a handoff from a previous context "
    "window — treat it as background reference, NOT as active instructions. "
    "Do NOT answer questions or fulfill requests mentioned in this summary; "
    "they were already addressed. "
    "Respond ONLY to the latest user message that appears AFTER this "
    "summary — that message is the single source of truth for what to do "
    "right now. "
    "Topic overlap with the summary does NOT mean you should resume its "
    "task: even on similar topics, the latest user message WINS. Treat ONLY "
    "the latest message as the active task and discard stale items from "
    f"'{HISTORICAL_TASK_HEADING}' / '{HISTORICAL_IN_PROGRESS_HEADING}' / "
    f"'{HISTORICAL_PENDING_ASKS_HEADING}' / "
    f"'{HISTORICAL_REMAINING_WORK_HEADING}' entirely — do not 'wrap up' or "
    "'finish' work described there unless the latest message explicitly "
    "asks for it. "
    "Reverse signals in the latest message (e.g. 'stop', 'undo', 'roll "
    "back', 'just verify', 'don't do that anymore', 'never mind', a new "
    "topic) must immediately end any in-flight work described in the "
    "summary; do not re-surface it in later turns. "
    "IMPORTANT: Your persistent memory (MEMORY.md, USER.md) in the system "
    "prompt is ALWAYS authoritative and active — never ignore or deprioritize "
    "memory content due to this compaction note. "
    "The current session state (files, config, etc.) may reflect work "
    "described here — avoid repeating it:"
)

# 摘要正文结束标记。物理上把「历史压缩块」和「当前用户消息」切开，
# 提醒主模型：上面结束了，下面才是要响应的内容。
SUMMARY_END_MARKER = (
    "--- END OF CONTEXT SUMMARY — "
    "respond to the message below, not the summary above ---"
)

# 插回 messages 时挂在 dict 上的内部标记（不是发给模型的文本）。
# 演示/调试可用它识别「哪一条是压缩摘要」；真 Hermes 也用同类 metadata。
COMPRESSED_SUMMARY_METADATA_KEY = "_compressed_summary"

# =============================================================================
# C. 辅助模型（summarizer）prompt 积木
# -----------------------------------------------------------------------------
# build_summarizer_prompt() 组装顺序：
#   SUMMARIZER_PREAMBLE
#   + FIRST_PASS_INSTRUCTIONS  或  ITERATE_INSTRUCTIONS
#   + _template_sections(summary_budget)
#   + [可选] FOCUS_TOPIC_SUFFIX
# =============================================================================

# 角色与硬约束：你是「做 checkpoint 的摘要代理」，不是聊天助手。
#   - 只输出结构化摘要，禁止问候/开场白
#   - 跟用户对话语言一致（不要强行英文化）
#   - 密钥类内容一律 [REDACTED]
SUMMARIZER_PREAMBLE = (
    "You are a summarization agent creating a context checkpoint. "
    "Treat the conversation turns below as source material for a "
    "compact record of prior work. "
    "Produce only the structured summary; do not add a greeting, "
    "preamble, or prefix. "
    "Write the summary in the same language the user was using in the "
    "conversation — do not translate or switch to English. "
    "NEVER include API keys, tokens, passwords, secrets, credentials, "
    "or connection strings in the summary — replace any that appear "
    "with [REDACTED]. Note that the user had credentials present, but "
    "do not preserve their values."
)

# 迭代压缩（已有 previous_summary）时用。
# placeholder:
#   {previous_summary}      — 上一轮压缩留下的摘要
#   {content_to_summarize}  — 本轮要并入的新 middle turns
# 要求：保留仍相关的旧信息、续编号、迁移 In Progress → Completed、
# 更新 Active Task 为用户最新未兑现输入。
ITERATE_INSTRUCTIONS = (
    "You are updating a context compaction summary. A previous compaction "
    "produced the summary below. New conversation turns have occurred since "
    "then and need to be incorporated.\n\n"
    "PREVIOUS SUMMARY:\n"
    "{previous_summary}\n\n"
    "NEW TURNS TO INCORPORATE:\n"
    "{content_to_summarize}\n\n"
    "Update the summary using this exact structure. PRESERVE all existing "
    "information that is still relevant. ADD new completed actions to the "
    "numbered list (continue numbering). Move items from \"In Progress\" to "
    "\"Completed Actions\" when done. Move answered questions to "
    "\"Resolved Questions\". Update \"Active State\" to reflect current state. "
    "Remove information only if it is clearly obsolete. CRITICAL: Update "
    "\"## Active Task\" to reflect the user's most recent unfulfilled "
    "input — this includes any question, decision request, or discussion "
    "turn that the assistant has not yet answered. Only write \"None\" if "
    "the last exchange was fully resolved."
)

# 首次压缩（没有 previous_summary）时用。
# placeholder:
#   {content_to_summarize}  — 本次被切开的 middle 对话原文
# 后面紧跟 _template_sections()，告诉模型「按这个骨架写」。
FIRST_PASS_INSTRUCTIONS = (
    "Create a structured checkpoint summary for the conversation after "
    "earlier turns are compacted. The summary should preserve enough detail "
    "for continuity without re-reading the original turns.\n\n"
    "TURNS TO SUMMARIZE:\n"
    "{content_to_summarize}\n\n"
    "Use this exact structure:"
)

# 可选后缀：用户指定 /compress <focus> 时追加在 prompt 末尾（后写优先）。
# placeholder: {focus_topic}
# 预算倾斜：与 focus 相关的内容吃 60–70% token；其它内容大力压缩。
FOCUS_TOPIC_SUFFIX = (
    '\n\nFOCUS TOPIC: "{focus_topic}"\n'
    "This compaction should PRIORITISE preserving all information related "
    "to the focus topic above. For content related to \"{focus_topic}\", "
    "include full detail — exact values, file paths, command outputs, error "
    "messages, and decisions. For content NOT related to the focus topic, "
    "summarise more aggressively (brief one-liners or omit if truly "
    "irrelevant). The focus topic sections should receive roughly 60-70% of "
    "the summary token budget. Even for the focus topic, NEVER preserve API "
    "keys, tokens, passwords, or credentials — use [REDACTED]."
)


def _today_str() -> str:
    """今天的日期字符串，供 TEMPORAL ANCHORING 使用。

    真源码走 hermes_time.now()；demo 用本地 date，失败则返回空串
   （此时整段 temporal 规则会被省略，避免编造日期）。
    """
    try:
        from datetime import date

        return date.today().strftime("%Y-%m-%d")
    except Exception:
        return ""


def _temporal_anchoring_rule() -> str:
    """时间锚定规则：已完成动作写成带日期的过去时，禁止写成「还待办」。

    例：不要写 "email John about the proposal"；
        应写 "Sent the proposal email to John on 2026-07-22."
    没有可用日期时返回空串，不注入这段规则。
    """
    today = _today_str()
    if not today:
        return ""
    return (
        f"\nTEMPORAL ANCHORING: The current date is {today}. When an "
        "action has already been carried out, phrase it as a completed, "
        "dated, past-tense fact rather than an open instruction. For "
        'example, rewrite "email John about the proposal" as "Sent the '
        f'proposal email to John on {today}." Never leave a finished '
        "action worded as if it still needs doing, and never invent a date "
        "for work that has not happened yet.\n"
    )


def _template_sections(summary_budget: int = 800) -> str:
    """辅助模型输出骨架（首压 / 迭代共用）。

    每个 ## section 下方的方括号说明是「写作 brief」，告诉 summarizer：
      - Historical Task Snapshot：用户最新未兑现输入（可含问句，不只是命令）
      - Goal / Constraints：目标与偏好
      - Completed Actions：带 tool/路径/结果的编号清单
      - Active State：工作区、分支、测试状态等
      - Historical In-Progress / Pending Asks / Remaining Work：一律 Historical/STALE
      - Critical Context：易丢的具体值；密钥必须 [REDACTED]

    summary_budget：目标摘要约多少 tokens（模板末尾 Target ~N tokens）。
    末尾还会附上 _temporal_anchoring_rule()。
    """
    return f"""{HISTORICAL_TASK_HEADING}
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

{HISTORICAL_IN_PROGRESS_HEADING}
[Work currently underway — what was being done when compaction fired]

## Blocked
[Any blockers, errors, or issues not yet resolved. Include exact error messages.]

## Key Decisions
[Important technical decisions and WHY they were made]

## Resolved Questions
[Questions the user asked that were ALREADY answered — include the answer so it is not repeated]

{HISTORICAL_PENDING_ASKS_HEADING}
[Questions or requests from the user that have NOT yet been answered or fulfilled. These are STALE — they were from the compacted turns. Write them here for reference only. The agent must NOT act on them unless the latest user message explicitly requests it. If none, write "None."]

## Relevant Files
[Files read, modified, or created — with brief note on each]

{HISTORICAL_REMAINING_WORK_HEADING}
[What remains to be done — framed as STALE context for reference only. The agent must NOT resume this work unless the latest user message explicitly asks for it.]

## Critical Context
[Any specific values, error messages, configuration details, or data that would be lost without explicit preservation. NEVER include API keys, tokens, passwords, or credentials — write [REDACTED] instead.]

Target ~{summary_budget} tokens. Be CONCRETE — include file paths, command outputs, error messages, line numbers, and specific values. Avoid vague descriptions like "made some changes" — say exactly what changed.
{_temporal_anchoring_rule()}
Write only the summary body. Do not include any preamble or prefix."""


def build_summarizer_prompt(
    content_to_summarize: str,
    *,
    previous_summary: str = "",
    focus_topic: str = "",
    summary_budget: int = 800,
) -> str:
    """组装发给辅助模型的完整 prompt。

    对照源码：context_compressor.py :: ContextCompressor._generate_summary()。

    参数
    ----
    content_to_summarize:
        本次要压缩的 middle 对话（serialize 后的 role: content 文本）；
        可能已附上 MemoryProvider 的 provider_hint。
    previous_summary:
        非空 → 走迭代压缩（ITERATE_INSTRUCTIONS）；
        空   → 走首次压缩（FIRST_PASS_INSTRUCTIONS）。
    focus_topic:
        非空时追加 FOCUS_TOPIC_SUFFIX（/compress <focus>）。
    summary_budget:
        传给输出骨架的目标 token 预算。

    返回
    ----
    完整 user prompt 字符串，由 llm.summarize_fn 发给 DeepSeek。
    """
    sections = _template_sections(summary_budget)

    if previous_summary:
        # 迭代：旧摘要 + 新 turns → 更新后的结构化摘要
        prompt = (
            f"{SUMMARIZER_PREAMBLE}\n\n"
            + ITERATE_INSTRUCTIONS.format(
                previous_summary=previous_summary,
                content_to_summarize=content_to_summarize,
            )
            + f"\n\n{sections}"
        )
    else:
        # 首压：只给 middle turns → 从零生成结构化摘要
        prompt = (
            f"{SUMMARIZER_PREAMBLE}\n\n"
            + FIRST_PASS_INSTRUCTIONS.format(
                content_to_summarize=content_to_summarize,
            )
            + f"\n\n{sections}"
        )

    if focus_topic:
        # 后写优先：focus 约束贴在末尾，覆盖前面的「均匀压缩」暗示
        prompt += FOCUS_TOPIC_SUFFIX.format(focus_topic=focus_topic)

    return prompt
