# 03 · Session Key 与 Store

**何时使用**：解释「为什么同群不同人 / 同线程多人」会话是否共享。

## `build_session_key`（唯一真相源）

摘录：`excerpts/session_key_store.py`（对应 `session.py`）。

命名空间：`agent:main` 或 profile multiplex 前缀。

| chat_type | 关键规则 |
|-----------|----------|
| `dm` | `…:dm:<chat_id>`；无 chat_id 时用 participant，禁止全平台塌缩 |
| group/channel | `…:<chat_type>:<chat_id>[:thread][:user]` |
| thread | 默认 **不** append user（线程共享）；`thread_sessions_per_user` 才隔离 |

WhatsApp：对 JID/LID 做 `canonical_whatsapp_identifier`，避免同一人两条 key。

## `get_or_create_session`

- **Single-flight**：同 key 并发共用一次创建/切换结果  
- 内部 `_get_or_create_session_impl`：reset 策略、compression tip、SQLite I/O 尽量在锁外  

## session_key vs session_id

- Key = 路由（哪条对话线程）  
- Id = 当前 transcript 容器（`/new`、压缩续写会换 id）  

## 对照文件

- `hermes_src/gateway/session.py`（全文）  
- `hermes_src/gateway/excerpts/session_key_store.py`  
- 讲稿：[`../notes/2_session_and_history.md`](../notes/2_session_and_history.md)
