# 07 · Cron 挂在 Gateway 进程

**何时使用**：问「谁调用 `tick` / 为什么 messaging 挂了 cron 也不跑」。

## 启动（`start_gateway`）

摘录：`excerpts/run_message_and_cron.py` 后半。

```text
cron_provider = resolve_cron_scheduler()
Thread(cron_provider.start, cron_stop, name="cron-scheduler")
Thread(_start_gateway_housekeeping, cron_stop, …)
```

- **Cron tick** ≠ housekeeping：后者是频道目录刷新等网关杂务。  
- `_start_cron_ticker`：兼容 shim → `InProcessCronScheduler().start(...)`。

## 关闭

`_await_thread_exit`：用 `asyncio.sleep` 轮询，**禁止**在 loop 线程里同步 `join`——否则 in-flight 投递（`schedule_threadsafe` + `future.result`）会死锁丢消息（#58818）。

## 与 06-cron 模块分工

| 问题 | 读哪 |
|------|------|
| jobs.json / parse_schedule / run_job | [`../../06-cron/`](../../06-cron/) |
| 谁在进程里 `start()` provider | **本 catalog** |
| 结果怎么送到 Telegram | catalog `06` Delivery |

## 对照文件

- `excerpts/run_message_and_cron.py`
- 真仓：`cron/scheduler_provider.py`、`cron/scheduler.py`
