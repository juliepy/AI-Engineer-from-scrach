# Agent Loop Workflow

```text
fixtures/
  MEMORY.md + USER.md  → TeachingMemoryStore → frozen system (+ tools guidance)
  conversation_history.md → prior turns (no system row)

DemoAgent.run_conversation(user, history, system)
        │
        ▼
conversation_loop.run_conversation
        ├─ messages = history + current user
        ├─ IterationBudget(max_iterations=6)
        └─ while …:
              DeepSeek(+ todo, web_search)
              tool_calls? → invoke_tool → role=tool → continue
              text? → final_response
```

- model: `deepseek-v4-pro`
- web backend: `ddgs`
- exit_reason: `budget_grace_call`
- api_calls: `7`
- budget used/max: `6/6`
- tools: `['todo', 'web_search']`
- history_before_turn: `7`
- memory/user entries: `2` / `2`

## Role timeline

```text
  [0] user
  [1] assistant
  [2] user
  [3] assistant
  [4] user
  [5] assistant
  [6] user
  [7] user
  [8] assistant tool_calls=['todo']
  [9] tool name=todo
  [10] assistant tool_calls=['web_search', 'web_search']
  [11] tool name=web_search
  [12] tool name=web_search
  [13] assistant tool_calls=['web_search']
  [14] tool name=web_search
  [15] assistant tool_calls=['web_search']
  [16] tool name=web_search
  [17] assistant tool_calls=['todo']
  [18] tool name=todo
  [19] assistant tool_calls=['todo']
  [20] tool name=todo
  [21] assistant
```
