# Invariant Checks

对照 AGENTS.md：断言关系，不冻结快照。

## Layer A · pytest contracts（近 Hermes CI）

- result: `PASS`
- file: `teaching/invariants/test_agent_loop_contracts.py`

```text
................                                                         [100%]
16 passed in 0.06s
```

## Anti-patterns（不要写）

- `assert exit_reason == "budget_grace_call"  # 冻结某次实跑结果`
- `assert api_calls == 7  # 换模型/换 prompt 就会漂`
- `assert tool_sequence == ["todo", "web_search", ...]  # 精确序列快照`

## Layer B · offline case scores

### `golden-loop-ok` — PASS

- ✓ `tools_subset`: ok
- ✓ `no_forbidden`: ok
- ✓ `steps`: api_calls=7 max_steps=10
- ✓ `exit`: exit_reason='budget_grace_call' allowed=['budget_grace_call', 'completed']
- ✓ `final_text`: ok
- ✓ `role_alternation`: ok
- ✓ `system_stable`: stable across 6 api_requests
- ✓ `tools_frozen`: frozen ['todo', 'web_search']
- ✓ `budget_consistent`: ok

### `failure-wrong-tool-cache-break` — FAIL

- ✗ `tools_subset`: missing expected tools: ['todo', 'web_search']
- ✗ `no_forbidden`: forbidden used: ['execute_code']
- ✓ `steps`: api_calls=3 max_steps=4
- ✗ `exit`: exit_reason='budget_exhausted' allowed=['budget_grace_call', 'completed']
- ✗ `final_text`: empty final_response
- ✗ `role_alternation`: messages[5]: consecutive role='assistant' (prev also 'assistant')
- ✗ `system_stable`: api#2 system fingerprint 'chars:180' != 'chars:100'
- ✗ `tools_frozen`: api#2 tools ['execute_code', 'todo', 'web_search'] != ['todo', 'web_search']
- ✗ `budget_consistent`: exhausted but budget_used 2 < max 3
