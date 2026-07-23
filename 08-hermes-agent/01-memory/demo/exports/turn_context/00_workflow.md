# Turn Context Workflow

```text
load fixtures/
  MEMORY.md + USER.md  → TeachingMemoryStore.load_from_disk()
                       → frozen blocks → system_prompt (cached)
  long_conversation.md → conversation_history (no system row)

build_turn_context(...)
  ├─ append user message
  ├─ active_system_prompt = cached (MEMORY+USER)
  ├─ preflight estimate ~1547 tokens
  ├─ should_compress? → True
  ├─ compress middle → SUMMARY_PREFIX message
  │     (+ on_pre_compress hint from MEMORY/USER)
  ├─ memory prefetch
  └─ return TurnContext(messages=4)
```

- turn_id: `demo-session:demo-turn:dfcb5944`
- compressed: `True`
- tokens before/after: `1547` → `1547`
- model: `deepseek-v4-pro`
- memory entries: `2` / user entries: `2`
