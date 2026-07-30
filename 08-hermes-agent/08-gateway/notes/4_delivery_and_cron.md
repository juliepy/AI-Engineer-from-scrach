# 4 · Delivery 与同进程 Cron

对照 catalog：[`06_delivery_home.md`](../catalog/06_delivery_home.md)、[`07_cron_in_gateway.md`](../catalog/07_cron_in_gateway.md)。  
Cron 本体：[`../../06-cron/`](../../06-cron/)。

## Home Channel

`PlatformConfig.home_channel` / `GatewayConfig.get_home_channel(platform)`：

- Cron、部分后台通知的**默认投递落点**  
- 配置：`hermes setup gateway` / `config.yaml` / `*_HOME_CHANNEL`（插件可声明 `cron_deliver_env_var`）  
- 「本地文件」始终可落 `{HERMES_HOME}/cron/output`

## DeliveryRouter

`gateway/delivery.py`：

1. 解析 target（显式 `telegram:chat_id`、平台 Home、origin、local）  
2. `deliver()` 逐个 target 发送；已知 dead target 跳过（防刷洪）  
3. 超长输出有 gateway 级截断；会 chunk 的 adapter 可绕过

Agent 对用户的**同步回复**通常走 Adapter `send()`，不经过 cron DeliveryRouter；Router 更偏 **异步结果 / 定时任务**。

## Cron 挂在 Gateway 上

`start_gateway()`：

```text
cron_provider = resolve_cron_scheduler()
Thread(target=cron_provider.start, args=(cron_stop,), name="cron-scheduler")
Thread(target=_start_gateway_housekeeping, …)   # 目录刷新等，不是 tick 本身
```

要点：

- Cron **与 messaging 同进程**，共享 adapters / loop（投递要 `schedule_threadsafe`）。  
- 关闭时不能 `join()` 卡死事件循环（见 `_await_thread_exit` 注释）。  
- 旧符号 `_start_cron_ticker` 是兼容 shim → `InProcessCronScheduler`。

无平台也可只为 cron 保活 gateway（日志里有「continue for cron」路径）。

## 新平台与投递

加渠道优先 **plugin**（`ADDING_A_PLATFORM.md`）：

- `ctx.register_platform(...)`  
- 可选 `standalone_sender_fn`：gateway 未在线时 cron 仍能发  
- 可选 `cron_deliver_env_var`：Home 解析不用改 `cron/scheduler.py` 硬编码

## 收束

学完应能口述：

1. 入站：`handle_message` → `_handle_message` → session → `AIAgent`  
2. 双守卫 + bypass  
3. session_key vs session_id  
4. cron 在 gateway 线程里 tick，结果经 DeliveryRouter / Home 出去
