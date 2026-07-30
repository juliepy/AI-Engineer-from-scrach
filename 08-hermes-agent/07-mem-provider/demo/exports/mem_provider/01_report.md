# Mem-provider demo

- hermes_agent_root: `D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent`
- generated: 2026-07-30T02:49:58.352164+00:00

## 1. Prefetch → user injection (fetch)

```
<memory-context>
[System note: The following is recalled memory context, NOT new user input. Treat as authoritative reference data — this is the agent's persistent memory and should inform all responses.]

User previously said they like short answers. (query='What did I say about reply length?')
</memory-context>
```

## 2. System prompt block (static)

```
## Fake memory backend
Use recalled facts from <memory-context>.
```

## 3. After turn: sync_turn (store)

```json
[
  {
    "user": "What did I say about reply length?",
    "assistant": "You prefer concise replies.",
    "session_id": "demo-sess"
  }
]
```

## Related prompts (read in notes/04)

- `MEMORY_GUIDANCE`
- `_MEMORY_REVIEW_PROMPT`
- `<memory-context>` system note
