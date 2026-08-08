# Mem0 OSS demo (local)

- hermes_agent_root: `D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent`
- HERMES_HOME (isolated): `D:\workspace\doc\面试狂魔\人工智能面试题\AI_coding_interview\08-hermes-agent\07-mem-provider\demo\.hermes_demo`
- backend: `deepseek (https://api.deepseek.com) + ollama-embed (nomic-embed-text @ http://localhost:11434) + local qdrant`
- generated: 2026-08-02T13:31:52.300282+00:00
- sync_joined: `True`

## 1. Store — sync_turn (infer=True) + mem0_add

Turn 1 goes through `MemoryManager.sync_all` → `Mem0MemoryProvider.sync_turn`
→ OSS `backend.add(..., infer=True)` (LLM fact extraction).

```json
{"result": "Fact stored.", "event_id": null}
```

## 2. Fetch — prefetch → `<memory-context>` fence

```
<memory-context>
[System note: The following is recalled memory context, NOT new user input. Treat as authoritative reference data — this is the agent's persistent memory and should inform all responses.]

## Mem0 Memory
- User prefers short answers in Chinese. Project codename is Orion.
- User prefers short answers in Chinese. Project codename is Orion.
- User prefers short answers in Chinese. Project codename is Orion.
</memory-context>
```

## 3. mem0_search tool (same OSS backend)

```json
{"results": [{"id": "581b005a-7700-4fdf-b87f-21c981535af6", "memory": "User prefers short answers in Chinese. Project codename is Orion.", "score": 0.3146232808925302}, {"id": "8cce0989-4863-4d56-b925-46dfc5529467", "memory": "User prefers short answers in Chinese. Project codename is Orion.", "score": 0.3146232805964491}, {"id": "3755743d-c398-444e-b01e-497d5cd58fd9", "memory": "User prefers short answers in Chinese. Project codename is Orion.", "score": 0.3082522199868039}], "count": 3}
```

## 4. System prompt block

```
# Mem0 Memory
Active. Mode: OSS (self-hosted). User: mem0-demo-user.
You have persistent memory of this user from past conversations. You should call mem0_search before answering anything that could depend on prior context (the user's preferences, facts, history, people, projects, or earlier decisions) — do not rely on the chat window alone, and do not assume you have no memory.
For multi-part or multi-hop questions, run several searches with different wording/angles and follow-up searches on what the first results surface; one search is rarely enough. Keep searching until you have every fact the question needs before you answer.
Tools: mem0_search to find memories, mem0_add to store facts, mem0_update and mem0_delete to manage by ID.
```
