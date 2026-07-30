# Eval Suite Workflow

```text
Layer A  pytest teaching/invariants/test_agent_loop_contracts.py
         （Hermes 风格：Test* 类 + 关系断言）
      │
Layer B  fixtures/eval_cases.json
         + from_02_agent_loop.json（正例）
         + failure_run.json（负例）
      │
      ▼
score_suite()  →  tools / steps / exit / invariants
      │
      ├─ session_logger demo (session_tag)
      └─ RCA on failing cases
```

- pytest_contracts: `PASS`
- offline cases: `2`
- offline passed: `1`
- offline failed: `1`
- session_demo: `sess_eval_demo`
- offline: `true`（无 API Key）

## Case summary

| case | pass | exit | api_calls | tools |
|------|------|------|-----------|-------|
| `golden-loop-ok` | True | `budget_grace_call` | 7 | `todo,web_search,web_search,web_search,web_search,todo,…` |
| `failure-wrong-tool-cache-break` | False | `budget_exhausted` | 3 | `execute_code` |
