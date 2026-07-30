# 3 · 双层忙时守卫（面试高频）

对照 catalog：[`04_dual_guards.md`](../catalog/04_dual_guards.md)、[`05_slash_bypass.md`](../catalog/05_slash_bypass.md)。  
根因级说明亦见上游 `AGENTS.md`：「The gateway has TWO message guards」。

## 为什么要两层

Agent 跑着时用户又发消息：可能是跟进、也可能是 `/stop`、也可能是 `/approve`（线程堵在 `Event.wait`）。

| 行为 | 正确做法 | 错误做法 |
|------|----------|----------|
| 普通跟进 | 进 pending，当前 Turn 结束后 cascade | 并行再开一个 Agent（打乱 transcript / cache） |
| `/stop` `/new` | **立刻**进 runner，取消 inflight | 排进 pending → 变成用户文本或丢弃 |
| `/approve` `/deny` | **立刻**进 runner 解阻塞 | 排队 → **死锁**（Agent 永远等不到批准） |
| clarify 选项答复 | 当「解阻塞」 bypass，同 approve | 当成新 Turn 排队 |

## ① Adapter：`_active_sessions`

位置：`BasePlatformAdapter.handle_message`。

```text
if session_key in self._active_sessions:
    if should_bypass_active_session(cmd):
        # inline 调 _message_handler；/stop|/new 走专用 handoff
        # 禁止走 _process_message_background（会抢 session lifecycle）
    elif clarify pending:
        # 同样 inline
    else:
        merge → _pending_messages[session_key]
        return
# else: 同步安装 guard，再 spawn background
```

`should_bypass_active_session`：**任意能 resolve 的 slash 命令**都 bypass（见 `hermes_cli/commands.py`）。理由：已识别的 `/xxx` 排队后会被安全网丢掉，表现为「零字回复」。

## ② Runner：`_running_agents` + busy handler

Adapter 放行后，Runner 仍可能看到「本 session 已有 AIAgent 在跑」：

- `busy_input_mode` / `busy_text_mode`：`interrupt` | `queue` | `steer` 等  
- `/steer` → `running_agent.steer(text)`  
- `/queue` → 独立 FIFO（不要和单槽 `_pending_messages` 合并语义搞混）

控制命令仍由 slash handler 处理；**不要**再包一层会管理 session 生命周期的 background task。

## 记忆口诀

> **两层都要 bypass；解阻塞类命令必须 inline。**

## 下一步

→ [`4_delivery_and_cron.md`](./4_delivery_and_cron.md)
