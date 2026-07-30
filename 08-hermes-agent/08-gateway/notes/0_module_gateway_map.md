# 0 · Gateway 模块地图

先建立「文件职责」再下钻热路径。完整对照：[`../hermes_src/`](../hermes_src/README.md)。

## 核心对象

| 对象 | 文件 | 一句话 |
|------|------|--------|
| `GatewayRunner` | `run.py` | 生命周期 + 路由消息到 Agent + slash mixin |
| `BasePlatformAdapter` | `platforms/base.py` | 平台 I/O 统一口；第一层忙时守卫 |
| `SessionStore` | `session.py` | routing key → session_id；reset 策略 |
| `build_session_key` | `session.py` | **唯一** session key 构造入口 |
| `GatewayConfig` / `Platform` | `config.py` | 平台开关、Home channel、reset policy |
| `DeliveryRouter` | `delivery.py` | Cron / 指定 target 出站 |
| `platform_registry` | `platform_registry.py` | 插件平台自注册（延迟加载） |

## 目录分层（真仓）

```text
gateway/
├── run.py                 # ★ GatewayRunner + start_gateway
├── session.py             # ★ SessionStore / build_session_key
├── config.py              # Platform / HomeChannel / load_gateway_config
├── delivery.py            # DeliveryRouter
├── platform_registry.py   # 插件平台发现
├── slash_commands.py      # /命令 mixin（挂到 Runner）
├── authz_mixin.py / …     # 授权、kanban watchers、status…
├── platforms/
│   ├── base.py            # ★ BasePlatformAdapter
│   ├── ADDING_A_PLATFORM.md
│   └── signal / weixin / webhook / …   # 部分内置
└── builtin_hooks/         # 网关级 hook 扩展点

plugins/platforms/<name>/  # Telegram / Discord / … 多数渠道在这里
```

**现实**：不是一个万能适配器；Telegram/Discord 等走 **plugin**（`plugins/platforms/`），内置文件保留 signal/weixin/webhook 等。见 catalog `08`。

## Mixin 拼装

```text
GatewayRunner(
  GatewayAuthorizationMixin,   # 用户/群授权、pairing
  GatewayKanbanWatchersMixin,
  GatewaySlashCommandsMixin,   # slash_commands.py
)
```

读 `/stop` `/approve` 时：先看 `hermes_cli/commands.py` 的 bypass 判定，再落到 `slash_commands.py` / `run.py` 的 Level-2 handler。

## 启动入口

```text
hermes gateway  →  gateway.run:main()
                →  start_gateway()
                    ├─ 建 GatewayRunner，连各 adapter
                    ├─ CronScheduler provider 后台线程
                    └─ housekeeping 线程（非 cron tick）
```

Cron 细节见 [`../../06-cron/`](../../06-cron/)；本模块只钉「**谁在 gateway 进程里启动它**」。

## 下一步

→ [`1_message_pipeline.md`](./1_message_pipeline.md)
