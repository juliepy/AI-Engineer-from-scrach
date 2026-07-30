# 2 · Session Key 与历史容器

对照 catalog：[`03_session_key.md`](../catalog/03_session_key.md)。  
鸟瞰：[`../../01-arch.md`](../../01-arch.md) §5.3。

## Session Key ≠ Session ID

| 概念 | 是什么 | 谁生成 |
|------|--------|--------|
| **session_key** | **路由键**：同线程对话的稳定字符串 | `build_session_key(SessionSource)` |
| **session_id** | **transcript 行 / SQLite 主键** | `SessionStore` 创建/切换时 |

一个 key 可在 `/new`、压缩续写后映射到**新的** `session_id`；routing 仍用同一 key。

典型形状（另有 profile 命名空间前缀）：

```text
agent:main:telegram:dm:<chat_id>
agent:main:telegram:group:<chat_id>:<user_id>     # 群默认按人隔离
agent:main:telegram:group:<chat_id>:<thread_id>   # 论坛主题：默认线程内共享
```

规则摘要（详见源码 docstring）：

- **DM**：优先 `chat_id`；缺省时用 participant，避免多人塌缩进同一 `…:dm`。
- **Group**：`group_sessions_per_user` 默认 True → 群里每人一条会话。
- **Thread**：默认 **不**按人隔离（整条 thread 共享），除非 `thread_sessions_per_user`。

**唯一入口**：`gateway/session.py::build_session_key`——不要在适配器里手搓 key。

## SessionStore 职责

1. `get_or_create_session(source)` — single-flight，同 key 并发只建一次。  
2. Reset policy（idle / daily / …）——到期 `force_new`。  
3. 与 SQLite / compression tip 对齐：压缩后绑定要指到 tip，避免复活 oversized 父会话。  
4. `build_session_context_prompt` — 告诉 Agent「你在哪个平台/群/线程」（进 context 层，注意 cache 语义）。

## 和 Prompt Cache 的关系

- Gateway 用 `_agent_cache[session_key] = (AIAgent, signature)` 复用实例。  
- `/new`、换 model、换 toolset 等会换 signature → 新 Agent → **新**缓存前缀（故意）。  
- 中途不要重建 SP；记忆更新走 user 注入 / tool 返回（见 `07-mem-provider`）。

## 跨会话泄漏防护

`_handle_message` 入口调用 `reset_session_vars()`：asyncio `create_task` 会 copy ContextVar，若不重置，子进程环境可能读到**兄弟 session** 的身份。见 `session_context.py`。

## 下一步

→ [`3_concurrency_guards.md`](./3_concurrency_guards.md)
