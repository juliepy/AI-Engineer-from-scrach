# 02 · 消息热路径

**何时使用**：要讲清「Telegram 一条消息怎么进 `run_conversation`」。

## 热路径图

```text
MessageEvent
  → handle_message                    # platforms/base.py
  → [_pending | bypass | background]
  → GatewayRunner._handle_message     # run.py
  → _handle_message_with_agent
  → SessionStore.get_or_create_session
  → AIAgent（_agent_cache）
  → adapter.send
```

## Adapter 入口要点

`handle_message`（摘录 `excerpts/base_handle_message.py`）：

1. `build_session_key(event.source, …)`  
2. 忙：`should_bypass_active_session` → **inline** `_message_handler`（尤其 `/stop`/`/new` 走 handoff）  
3. 忙：clarify pending → inline  
4. 忙：否则 `merge_pending_message_event` → return  
5. 闲：`_start_session_processing` **同步**装 `_active_sessions`，再 background

## Runner 入口要点

`_handle_message`（摘录 `excerpts/run_message_and_cron.py`）：

1. `reset_session_vars()` — 防 ContextVar 继承兄弟会话  
2. startup restore 期间：真人消息先入队  
3. `pre_gateway_dispatch` hook（可 skip/rewrite）  
4. 授权 / pairing  
5. 其后：slash → busy → `_handle_message_with_agent`

`_handle_message_with_agent`：`get_or_create_session` → 绑定 session →（后续）组历史、跑 Agent。

## 对照文件

- `hermes_src/gateway/excerpts/base_handle_message.py`
- `hermes_src/gateway/excerpts/run_message_and_cron.py`
- 讲稿：[`../notes/1_message_pipeline.md`](../notes/1_message_pipeline.md)
