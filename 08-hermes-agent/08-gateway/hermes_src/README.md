# hermes_src · Gateway 对照源码

来自完整仓 `hermes-agent/gateway/`（及少量 `hermes_cli/commands.py` 摘录）。

## 布局

| 路径 | 说明 |
|------|------|
| `gateway/__init__.py` | 对外导出：Config / Session / Delivery |
| `gateway/config.py` | `Platform` / `HomeChannel` / `GatewayConfig`（全文拷贝） |
| `gateway/session.py` | `build_session_key` / `SessionStore`（全文拷贝） |
| `gateway/delivery.py` | `DeliveryRouter`（全文拷贝） |
| `gateway/platform_registry.py` | 插件平台注册表 |
| `gateway/session_context.py` | ContextVars：防跨 session 泄漏 |
| `gateway/platforms/ADDING_A_PLATFORM.md` | **推荐走 plugin**，不要改 core |
| （真仓）`gateway/slash_commands.py` | Runner mixin：大量 `/` 命令；体量大，**不拷贝**，按符号在完整仓搜 |
| `gateway/excerpts/` | `run.py` / `base.py` 等巨文件**按行号摘录** |

## 巨文件策略

| 真仓文件 | 体量 | 本目录 |
|----------|------|--------|
| `gateway/run.py` | ~20k 行 | `excerpts/run_*.py` |
| `gateway/platforms/base.py` | ~5k+ 行 | `excerpts/base_handle_message.py` |
| `hermes_cli/commands.py` | 大 | `excerpts/commands_bypass.py` |

断点、全文件导航请打开完整 `hermes-agent`，行号以 excerpts 注释 `===== lines A-B =====` 为准（上游漂移时重跑 `scripts/extract_gateway_map.py`）。

## 不要

- 不要 `import hermes_src.gateway…` 当可运行包。
- 不要指望 excerpts 可独立执行。
