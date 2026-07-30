# 06 · Delivery 与 Home Channel

**何时使用**：讲 Cron 结果 / 指定 `deliver=` 怎么落到某个 chat。

## HomeChannel

`config.py`（摘录 `excerpts/config_platform_home.py`）：

- 挂在 `PlatformConfig.home_channel`  
- `GatewayConfig.get_home_channel(platform)` 查询  

用途：无人值守输出的默认「家」；setup 向导会引导设置。

## DeliveryRouter.deliver

摘录：`excerpts/delivery_router.py`。

```text
for target in targets:
  if dead_targets.is_dead(...): skip
  if LOCAL: 写 {HERMES_HOME}/cron/output
  else: adapter / standalone_sender 发送
  成功则 clear dead flag
```

辅助：

- `MAX_PLATFORM_OUTPUT`：非 chunking 平台截断头  
- `_is_silence_narration`：过滤纯 “silent” 废话，避免刷屏  

## 和用户 Turn 回复的区别

| 路径 | 机制 |
|------|------|
| 用户问一句 | `_process_message_background` → `adapter.send` |
| Cron / 显式 target | `DeliveryRouter`（可能无 live adapter → plugin `standalone_sender_fn`） |

## 对照文件

- `hermes_src/gateway/delivery.py`
- `hermes_src/gateway/excerpts/config_platform_home.py`
- 讲稿：[`../notes/4_delivery_and_cron.md`](../notes/4_delivery_and_cron.md)
