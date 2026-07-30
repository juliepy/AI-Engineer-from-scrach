# 02 · Prefetch：对话取上下文时如何 fetch mem

> 对照：  
> - [`../hermes_src/excerpts/turn_context.PREFETCH.py`](../hermes_src/excerpts/turn_context.PREFETCH.py)  
> - [`../hermes_src/excerpts/conversation_loop.INJECT.py`](../hermes_src/excerpts/conversation_loop.INJECT.py)  
> - `memory_manager.prefetch_all` / `build_memory_context_block`  
> 下一篇：[`03_sync_turn_store.md`](./03_sync_turn_store.md)

---

## 一句话

外部记忆的 **动态召回** 不进 system prompt（否则打 cache）。  
Turn 开头 `prefetch_all(user_msg)` 一次 → 结果缓存在 `TurnContext.ext_prefetch_cache` → 每次调 LLM 前拼进 **当前 turn 的 user message**（仅 API 副本，不写回 session DB）。

---

## 调用时序

```text
run_conversation / turn prologue (turn_context.py)
  ├─ on_turn_start(turn, user_msg)     # provider 计数 / 维护
  └─ ext_prefetch_cache = prefetch_all(user_msg)

conversation_loop → 组装 api_messages
  └─ 当前 turn 的 user msg 副本:
         content += "\n\n" + <memory-context>…</memory-context>
         （原 messages 列表不 mutate → 会话持久化干净）
```

注释原文要点：

> External recall context is injected into the **user message**, not the system prompt,  
> so the stable cache prefix remains unchanged.

---

## 围栏格式（`build_memory_context_block`）

```text
<memory-context>
[System note: The following is recalled memory context,
NOT new user input. Treat as authoritative reference data — ...]

{provider prefetch text}
</memory-context>
```

- `sanitize_context` 会剥掉 provider 自己塞进来的假 fence，防套娃 / 注入。  
- 流式输出用 `StreamingContextScrubber`，避免模型回显围栏时泄漏到 UI。

---

## Builtin 怎么「取」？

Builtin **不是**每轮 prefetch：

- Session 启动：`MemoryStore.format_for_system_prompt("memory"|"user")` 写入 SP **volatile** 层（冻 snapshot）。  
- 模型需要新增事实 → 调 `memory` 工具写盘；**当前 session 的 SP 仍是旧 snapshot**。  
- 下一 session / 重建 SP 才看到新条目。

对比：

| | Builtin md | External prefetch |
|--|------------|-------------------|
| 频率 | 每 session 冻一次 | 每 turn 一次 |
| 位置 | system prompt | user message 尾部 |
| 对 cache | volatile 仍在 SP 串里，但整段 SP 会话内稳定 | 完全不碰 SP |

---

## 面试三句

1. Fetch = `MemoryManager.prefetch_all` → 围栏 → 拼到本轮 user。  
2. 故意不进 SP，保住 prompt cache。  
3. Builtin 画像走 SP snapshot；外部召回走 ephemeral user 注入。
