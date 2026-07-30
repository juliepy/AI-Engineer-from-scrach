# 03 · sync_turn：一个 turn 结束如何存储 mem

> 对照：  
> - [`../hermes_src/excerpts/turn_finalizer.SYNC.py`](../hermes_src/excerpts/turn_finalizer.SYNC.py)  
> - [`../hermes_src/excerpts/run_agent.SYNC_HELPER.py`](../hermes_src/excerpts/run_agent.SYNC_HELPER.py)  
> - `memory_manager.sync_all` / `queue_prefetch_all`  
> - Builtin：`tools/memory_tool.py`  
> 下一篇：[`04_memory_prompts.md`](./04_memory_prompts.md)

---

## 一句话

Turn 正常结束后：`sync_all(user, assistant)` 把本轮镜像进外部 backend（异步），并 `queue_prefetch_all(user)` 暖下一轮。  
**Interrupted turn 整段跳过**——半截回复不是可持久真相。

---

## 外部 Provider 路径

```text
turn_finalizer
  └─ agent._sync_external_memory_for_turn(...)
        if interrupted: return
        if not (manager and final_response and original_user_message): return
        sync_all(user_text, response_text, session_id, messages?)
        queue_prefetch_all(user_text, session_id)
```

| 步骤 | 作用 |
|------|------|
| `sync_turn(user, asst, messages=…)` | Provider 落库 / 向量化 / 图谱更新（应非阻塞） |
| `queue_prefetch(query)` | 后台召回，下轮 `prefetch()` 直接吃缓存 |

用 `original_user_message`，不用可能带 skill 展开的 `user_message`。  
多模态 content 会先 flatten 成纯文本。

`MemoryManager.sync_all` 在后台 worker 跑——慢后端不能把 UI 卡在「running」。

---

## Builtin 路径（另一条写）

Builtin **不**靠 `sync_turn` 自动摘要整轮对话，而是：

1. **显式**：模型在 turn 内调 `memory(action=add|replace|remove)` → 立刻写 `MEMORY.md` / `USER.md`。  
2. **周期审查**：turn 末若触发 `should_review_memory` → `_spawn_background_review` 用 `_MEMORY_REVIEW_PROMPT` 再开一轮 aux，可能再调 `memory` 工具。  
3. **镜像**：若有外部 provider，builtin 写入可通过 `on_memory_write` 通知外部。

Session 边界才有 `on_session_end`（CLI exit / reset / gateway 过期）——**不是**每个 turn。

---

## 不写 / 少写的场景

| 场景 | 行为 |
|------|------|
| `interrupted=True` | 不 sync、不 queue prefetch |
| `skip_memory=True`（cron / leaf subagent） | 通常不挂 manager 或 provider 跳过写 |
| 空 user / 空 final_response | helper 直接 return |
| Skill 无指令裸调用 | `_strip_skill_scaffolding` → skip |

---

## 和 Prompt Cache 的关系

- Mid-session builtin 写盘 **不刷新** SP → cache 前缀稳定。  
- External sync 在 turn **之后**，不影响本轮已发出的 messages。  
- 下一轮才用新的 prefetch /（新 session 才用新 SP snapshot）。

下一篇：这些路径上挂着哪些 prompt 文本。
