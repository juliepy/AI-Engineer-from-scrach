# 1 · 一条入站消息怎么变成 Turn

对照 catalog：[`02_message_path.md`](../catalog/02_message_path.md)、[`03_session_key.md`](../catalog/03_session_key.md)。

## 热路径（背这张）

```text
Platform SDK 回调
  → Adapter 构造成 MessageEvent
  → BasePlatformAdapter.handle_message
       · build_session_key(source)
       · 若 session 忙：bypass 控制命令 / 否则进 _pending_messages
       · 空闲：_start_session_processing → _process_message_background
  → message_handler = GatewayRunner._handle_message
       · reset_session_vars（防 ContextVar 跨会话泄漏）
       · pre_gateway_dispatch plugin hook
       · 授权 / pairing
       · slash 命令？→ 专用 handler，可能不进 Agent
       · 忙？→ runner busy（queue / interrupt / steer）
       · _handle_message_with_agent
            · get_or_create_session
            · 拉 SQLite 历史 + hygiene
            · 取/建缓存 AIAgent
            · run_conversation
  → Adapter send() 回渠道
```

## 为什么 Gateway「拼 Context」更重

| | CLI | Gateway |
|--|-----|---------|
| 进程 | 一次聊天一个进程/线程模型 | **常驻**，多 chat 并发 |
| 入站载荷 | 内存里已有完整 messages | **经常只有最新一条** |
| 历史 | 自然在 list 里 | **必须按 session_key → session_id 从 SQLite 拉** |
| System Prompt | 启动 freeze | 同样 freeze；靠 `_agent_cache` 保 prefix cache |

没有「拉历史」这一步，每条 Telegram 消息都会变成失忆新会话。

## 关键符号（打断点）

| 符号 | 文件 | 看什么 |
|------|------|--------|
| `handle_message` | `platforms/base.py` | 第一层守卫 + 派发 |
| `_handle_message` | `run.py` | 授权、命令、进 Agent 前闸门 |
| `_handle_message_with_agent` | `run.py` | session + AIAgent |
| `get_or_create_session` | `session.py` | routing → transcript 容器 |
| `start_gateway` | `run.py` | 进程级装配 |

摘录：`hermes_src/gateway/excerpts/base_handle_message.py`、`run_message_and_cron.py`。

## 内部事件

`event.internal=True`（如后台进程完成通知）**跳过用户授权**，但仍走同一 handler 骨架——别和真人消息的 pairing 路径搞混。

## 下一步

→ [`2_session_and_history.md`](./2_session_and_history.md)
