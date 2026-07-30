# 08 · 平台适配器与 Plugin 路径

**何时使用**：要加新 IM / 改发送行为；或解释「为什么 gateway/platforms 里没有 telegram.py」。

## 两条路

| 路径 | 位置 | 何时 |
|------|------|------|
| **Plugin（推荐）** | `plugins/platforms/<name>/` 或 `~/.hermes/plugins/` | 社区 / 第三方 / 新渠道 |
| Built-in | `gateway/platforms/*.py` | 已在核心树的少数适配器 |

官方说明全文：`hermes_src/gateway/platforms/ADDING_A_PLATFORM.md`。

## Plugin 最小面

1. 继承 `BasePlatformAdapter`  
2. `register(ctx)` → `ctx.register_platform(PlatformEntry(...))`  
3. 可选：`env_enablement_fn`、`apply_yaml_config_fn`、`cron_deliver_env_var`、`standalone_sender_fn`

**零改 core**：配置、授权、cron deliver、`send_message` 路由、setup 向导均可接 hook。

## BasePlatformAdapter 你要实现/关心的

- `connect` / `disconnect`  
- `send`（及图片/语音等可选）  
- 把 SDK 事件变成 `MessageEvent` 后调 `handle_message`  
- 凭证锁：`acquire_scoped_lock`（防两 profile 同 bot token）

忙时队列 / bypass **已在基类**，子类不要重新发明一套 pending。

## Registry

`platform_registry.register_deferred`：先登记 loader，真正 `create_adapter` 时再 import 重 SDK——加快非 gateway 的 `hermes` CLI 启动。

## 对照文件

- `hermes_src/gateway/platforms/ADDING_A_PLATFORM.md`
- `hermes_src/gateway/platform_registry.py`
- `hermes_src/gateway/excerpts/base_handle_message.py`（类头 + handle_message）
