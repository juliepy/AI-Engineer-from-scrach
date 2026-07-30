# 05 · Slash Bypass

**何时使用**：要精确回答「哪些命令能打断 busy session」。

## 源码位置

`hermes_cli/commands.py` 摘录：`excerpts/commands_bypass.py`。

## 两个集合

| 符号 | 含义 |
|------|------|
| `GATEWAY_KNOWN_COMMANDS` | 注册表里 gateway 可派发的 name+alias（含 config-gated） |
| `ACTIVE_SESSION_BYPASS_COMMANDS` | 有 **显式 Level-2 handler** 的子集（stop/approve/steer/…） |

## `should_bypass_active_session`

实现：**`resolve_command(name) is not None`** —— 任意可解析 slash 都 bypass，不限于 `ACTIVE_SESSION_BYPASS_COMMANDS`。

理由（源码注释）：已识别命令若进 pending，会被 runner 安全网丢弃 → 用户看到空回复；且 `/approve` 类会死锁。

未识别的自由文本：不 bypass → 进 pending / debounce。

## 与 Adapter 的配合

```text
cmd = event.get_command()
if should_bypass_active_session(cmd):
    if cmd in {stop, new, reset}:
        _dispatch_active_session_command(...)  # 取消 inflight + 保序
    else:
        await self._message_handler(event)     # approve/status/…
```

## 对照文件

- `hermes_src/gateway/excerpts/commands_bypass.py`
- 真仓全文：`hermes_cli/commands.py`（`COMMAND_REGISTRY`）
