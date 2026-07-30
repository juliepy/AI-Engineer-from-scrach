# 01 · Gateway 包地图

**何时使用**：刚进模块，先知道「改配置 / 改适配器 / 改路由」分别动哪。

## 导出面

`gateway/__init__.py` 对外主要是：

- Config：`GatewayConfig`、`PlatformConfig`、`HomeChannel`、`load_gateway_config`
- Session：`SessionStore`、`SessionContext`、`build_session_context_prompt`、`SessionResetPolicy`
- Delivery：`DeliveryRouter`、`DeliveryTarget`

**真正的大头** `GatewayRunner` / `start_gateway` 在 `run.py`，不从 `__init__` 再导一遍——CLI 入口直接 `from gateway.run import …`。

## Platform 枚举 + 插件

`config.py::Platform`：

- 内置成员：telegram、discord、signal、weixin、webhook…  
- `_missing_`：仅允许 **bundled plugin 名** 或 **registry 已注册** 名，防止任意字符串污染枚举。

`platform_registry.py`：

- `register` / `register_deferred`：插件启动时注册工厂  
- 延迟加载：避免每个 `hermes` 命令都 import 沉重 SDK  
- `create_adapter(name, config)`：统一实例化

## 启动

```text
start_gateway()
  · duplicate-instance guard（同 HERMES_HOME）
  · GatewayRunner(config)
  · 连接 adapters
  · cron provider 线程 + housekeeping 线程
  · 等到 shutdown → 协作式排空（勿阻塞 event loop）
```

## 对照文件

- `hermes_src/gateway/__init__.py`
- `hermes_src/gateway/platform_registry.py`
- `hermes_src/gateway/excerpts/config_platform_home.py`
