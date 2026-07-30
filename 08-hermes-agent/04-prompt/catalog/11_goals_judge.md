# /goal Continuation + Judge Prompts

> 源文件：`hermes_cli/goals.py`
> 共提取 **11** 个宏 / 模板块

## 何时使用

| 项 | 说明 |
|----|------|
| **类型** | ② Judge = Auxiliary；③ Continuation = 注入下一轮 **user**（有时叠 Kanban） |
| **时机** | 用户 `/goal` 立下长期目标后：循环「干活 → Judge 判 DONE/WAIT/CONTINUE → 必要时续跑 prompt」 |
| **Draft** | `DRAFT_CONTRACT_*` 在需要把目标写成可验收合同时用 |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","edgeLabelBackground":"#1a1a1a","fontSize":"15px"},"themeCSS":".edgeLabel,.edgeLabel p{color:#FFFFFF!important;fill:#FFFFFF!important}"}}%%
flowchart TB
    G["/goal 立目标"] --> WORK["主 Agent 干活"]
    WORK --> J["Judge 辅助模型<br/>JUDGE_*"]
    J -->|DONE| STOP["结束"]
    J -->|WAIT| ASK["等用户输入"]
    J -->|CONTINUE| CONT["CONTINUATION_PROMPT_*<br/>注入下一轮 user"]
    CONT --> WORK

    style J fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style CONT fill:#FFD54F,stroke:#F57F17,stroke-width:2px,color:#111111
    style WORK fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
```

## 索引

- [`CONTINUATION_PROMPT_TEMPLATE`](#continuation_prompt_template) — L71
- [`CONTINUATION_PROMPT_WITH_CONTRACT_TEMPLATE`](#continuation_prompt_with_contract_template) — L83
- [`CONTINUATION_PROMPT_WITH_SUBGOALS_TEMPLATE`](#continuation_prompt_with_subgoals_template) — L99
- [`JUDGE_SYSTEM_PROMPT`](#judge_system_prompt) — L112
- [`JUDGE_BACKGROUND_BLOCK_TEMPLATE`](#judge_background_block_template) — L155
- [`JUDGE_USER_PROMPT_TEMPLATE`](#judge_user_prompt_template) — L161
- [`JUDGE_USER_PROMPT_WITH_SUBGOALS_TEMPLATE`](#judge_user_prompt_with_subgoals_template) — L171
- [`JUDGE_USER_PROMPT_WITH_CONTRACT_TEMPLATE`](#judge_user_prompt_with_contract_template) — L193
- [`DRAFT_CONTRACT_SYSTEM_PROMPT`](#draft_contract_system_prompt) — L221
- [`KANBAN_GOAL_CONTINUATION_TEMPLATE`](#kanban_goal_continuation_template) — L1599
- [`KANBAN_GOAL_FINALIZE_TEMPLATE`](#kanban_goal_finalize_template) — L1611

---

## `CONTINUATION_PROMPT_TEMPLATE`

- 行号：`goals.py:71`

```text
[Continuing toward your standing goal]
Goal: {goal}

Continue working toward this goal. Take the next concrete step. If you believe the goal is complete, state so explicitly and stop. If you are blocked and need input from the user, say so clearly and stop.
```

---

## `CONTINUATION_PROMPT_WITH_CONTRACT_TEMPLATE`

- 行号：`goals.py:83`

```text
[Continuing toward your standing goal]
Goal: {goal}

Completion contract:
{contract_block}

Continue working toward the outcome above. Take the next concrete step. Stay within the stated boundaries and do not violate the constraints. Before claiming the goal is done, satisfy the Verification criterion and show the concrete evidence (command output, file contents, test result). If you hit the stated stop condition or are otherwise blocked and need user input, say so clearly and stop.
```

---

## `CONTINUATION_PROMPT_WITH_SUBGOALS_TEMPLATE`

- 行号：`goals.py:99`

```text
[Continuing toward your standing goal]
Goal: {goal}

Additional criteria the user added mid-loop:
{subgoals_block}

Continue working toward the goal AND all additional criteria. Take the next concrete step. If you believe the goal and every additional criterion are complete, state so explicitly and stop. If you are blocked and need input from the user, say so clearly and stop.
```

---

## `JUDGE_SYSTEM_PROMPT`

- 行号：`goals.py:112`

```text
You are a strict judge evaluating whether an autonomous agent has achieved a user's stated goal. You receive the goal text, the agent's most recent response, and — when present — a list of background processes the agent has running. Decide one of three verdicts.

DONE — the goal is fully satisfied:
- The response explicitly confirms the goal was completed, OR
- The response clearly shows the final deliverable was produced, OR
- The response explains the goal is unachievable / blocked / needs user input (treat this as DONE with reason describing the block).

WAIT — the goal is NOT done, but the next step is to wait for async work to finish rather than act again. Choose this ONLY when the agent's progress is genuinely gated on something running on its own:
- A background process listed below is still running AND the response shows the agent is waiting on its result (e.g. a CI poller, build, test run, deploy). If the process has a session id, return it in ``wait_on_session`` — that releases when the process exits OR its watch_patterns trigger fires (use this for a long-lived watcher that signals mid-run and may never exit). Otherwise return its pid in ``wait_on_pid`` (releases on exit only).
- The agent says it is rate-limited / backing off / must wait a fixed period — return seconds in ``wait_for_seconds``.
Picking WAIT parks the loop without burning a turn; it resumes automatically when the pid exits or the time elapses. Do NOT pick WAIT just because work remains — only when re-poking now would be pure busy-work because the agent can't progress until the async thing finishes.

CONTINUE — not done, and there is a concrete next step the agent can take right now. This is the default when in doubt.

Reply ONLY with a single JSON object on one line. Shapes:
{"verdict": "done", "reason": "<one sentence>"}
{"verdict": "continue", "reason": "<one sentence>"}
{"verdict": "wait", "wait_on_session": "<id>", "reason": "<one sentence>"}
{"verdict": "wait", "wait_on_pid": <int>, "reason": "<one sentence>"}
{"verdict": "wait", "wait_for_seconds": <int>, "reason": "<one sentence>"}
The legacy shape {"done": <true|false>, "reason": "..."} is still accepted (true=done, false=continue).
```

---

## `JUDGE_BACKGROUND_BLOCK_TEMPLATE`

- 行号：`goals.py:155`

```text
Background processes the agent currently has running (it may be waiting on one of these):
{background_lines}
```

---

## `JUDGE_USER_PROMPT_TEMPLATE`

- 行号：`goals.py:161`

```text
Goal:
{goal}

Agent's most recent response:
{response}

{background_block}Current time: {current_time}

Is the goal satisfied — done, continue, or wait?
```

---

## `JUDGE_USER_PROMPT_WITH_SUBGOALS_TEMPLATE`

- 行号：`goals.py:171`

```text
Goal:
{goal}

Additional criteria the user added mid-loop (all must also be satisfied for the goal to be DONE):
{subgoals_block}

Agent's most recent response:
{response}

{background_block}Current time: {current_time}

Decision: For each numbered criterion above, find concrete evidence in the agent's response that the criterion is satisfied. Do not accept generic phrases like 'all requirements met' or 'implying it was done' — require specific evidence (a file contents excerpt, an output line, a command result). If ANY criterion lacks specific evidence in the response, the goal is NOT done — return CONTINUE (or WAIT if blocked on a listed background process).

Is the goal AND every additional criterion satisfied?
```

---

## `JUDGE_USER_PROMPT_WITH_CONTRACT_TEMPLATE`

- 行号：`goals.py:193`

```text
Goal:
{goal}

Completion contract (the authoritative definition of done):
{contract_block}

Agent's most recent response:
{response}

{background_block}Current time: {current_time}

Decision rules:
- The goal is DONE only when the Verification criterion is satisfied AND the response shows concrete evidence of it (a command result, file contents excerpt, test/benchmark output) — not a claim like 'done' or 'all tests pass' without evidence.
- If any stated Constraint was violated, the goal is NOT done — CONTINUE.
- If the response shows the agent is waiting on a listed background process to satisfy the Verification criterion (e.g. CI is the verification and it's still running), return WAIT on that process instead of re-poking — re-poking now would be pure busy-work.
- If the response explains the work is blocked / unachievable / needs user input (e.g. the stated Stop condition was hit), treat it as DONE with the reason describing the block.
- Otherwise the goal is NOT done — CONTINUE.

Is the goal satisfied per its completion contract — done, continue, or wait?
```

---

## `DRAFT_CONTRACT_SYSTEM_PROMPT`

- 行号：`goals.py:221`

```text
You turn a user's plain-language objective into a structured completion contract for an autonomous coding agent. The contract has five fields:
- outcome: the single end state that must be true when done
- verification: the specific test / command / artifact that PROVES the outcome (must be concrete and checkable)
- constraints: what must NOT change or regress
- boundaries: which files, dirs, tools, or systems are in scope
- stop_when: the condition under which the agent should stop and ask for human input instead of pushing on

Infer sensible, specific values from the objective and any project context implied by it. Prefer concrete verification (a named test command, a build, a benchmark) over vague phrases. Keep each field to one or two sentences. If a field genuinely cannot be inferred, use an empty string for it.

Reply ONLY with a single JSON object on one line:
{"outcome": "...", "verification": "...", "constraints": "...", "boundaries": "...", "stop_when": "..."}
```

---

## `KANBAN_GOAL_CONTINUATION_TEMPLATE`

- 行号：`goals.py:1599`

```text
[Continuing toward this kanban task — judge says it is not done yet]
Reason: {reason}

Take the next concrete step toward completing the task. When the work is genuinely finished, call kanban_complete with a summary. If you are blocked and need human input, call kanban_block with a reason. Do not stop without calling one of them.
```

---

## `KANBAN_GOAL_FINALIZE_TEMPLATE`

- 行号：`goals.py:1611`

```text
[The work looks complete, but the task is still open]
Reason: {reason}

If the task is genuinely done, call kanban_complete now with a short summary of what you did. If something still blocks completion, call kanban_block with the reason instead.
```

---
