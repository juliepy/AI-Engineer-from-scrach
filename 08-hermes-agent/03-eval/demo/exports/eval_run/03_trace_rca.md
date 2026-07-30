# Trace RCA Reports

# Trace RCA

- case: `failure-wrong-tool-cache-break`
- root_cause: **wrong_tool+role_break+cache_break**
- exit_reason: `budget_exhausted`
- api_calls: `3`
- tool_sequence: `['execute_code']`

## Failed checks

- `tools_subset`
- `no_forbidden`
- `exit`
- `final_text`
- `role_alternation`
- `system_stable`
- `tools_frozen`
- `budget_consistent`

## Evidence

- tools_subset: missing expected tools: ['todo', 'web_search']
- no_forbidden: forbidden used: ['execute_code']
- exit: exit_reason='budget_exhausted' allowed=['budget_grace_call', 'completed']
- final_text: empty final_response
- role_alternation: messages[5]: consecutive role='assistant' (prev also 'assistant')
- system_stable: api#2 system fingerprint 'chars:180' != 'chars:100'
- tools_frozen: api#2 tools ['execute_code', 'todo', 'web_search'] != ['todo', 'web_search']
- budget_consistent: exhausted but budget_used 2 < max 3
- api#1 tool_calls=['execute_code']

## Fix hypothesis

- 模型选错工具或漏掉必要工具；对照 expected_tools / forbidden_tools
- 消息 role 交替被破坏（同 role 连发 / 中途插合成 user）→ 破 prompt cache 风险
- 同 turn 内 system 或 tools schema 变化 → prompt cache 失效
- 预算/退出理由异常：空转 tool 调用或未走 grace 收尾
- 无最终文本：可能卡在 tool_calls 或 interrupt

## Case notes

负例（合成）：错工具 + role 连发 + system/tools 漂移 + 无 grace。应 FAIL 并产出 RCA


---
