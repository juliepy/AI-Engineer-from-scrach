# 04 · 双层忙时守卫

**何时使用**：面试问「Agent 跑着用户又发 `/approve` 会怎样」。

## Level 1 — Adapter

状态：

- `_active_sessions: Dict[session_key, asyncio.Event]`  
- `_pending_messages: Dict[session_key, MessageEvent]`（单槽合并语义）

忙时分支见 `excerpts/base_handle_message.py` 中 `handle_message` 注释块（PR #4926 等）。

**硬规则**：bypass 路径 **禁止**调用 `_process_message_background`——它会管理 session lifecycle，与正在跑的 task 竞态。

## Level 2 — Runner

状态：

- `_running_agents: Dict[session_key, AIAgent | sentinel]`  
- `_queued_events`：`/queue` 专用 FIFO（与 adapter 单槽不同）  
- busy 模式：interrupt / queue / steer（摘录 `excerpts/run_busy_session.py`）

## 失败模式（曾经的 bug 类）

| 症状 | 根因 |
|------|------|
| `/approve` 后 Agent 永远卡住 | 批准消息进了 pending，解阻塞代码收不到 |
| `/stop` 变成普通用户词 | 未 bypass，排进下一轮 transcript |
| mid-run `/model` 零字回复 | 命令进 pending 后被安全网丢弃（#5057） |

## 对照文件

- `excerpts/base_handle_message.py`
- `excerpts/run_busy_session.py`
- 讲稿：[`../notes/3_concurrency_guards.md`](../notes/3_concurrency_guards.md)
