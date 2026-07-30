# 04 · 工厂与配置：`TERMINAL_ENV` → `_create_environment`

> 对照：[`../hermes_src/tools/terminal_tool.FACTORY.py`](../hermes_src/tools/terminal_tool.FACTORY.py)  
> 全文件：上游 / 完整仓 `tools/terminal_tool.py`（约 2.6k 行）  
> 包说明：[`../hermes_src/tools/environments/__init__.py`](../hermes_src/tools/environments/__init__.py)

---

## 一句话

行为配置在 **`config.yaml` 的 `terminal.*`**，桥成环境变量（如 `TERMINAL_ENV`）；  
`terminal_tool._get_env_config()` 读配置，`_create_environment()` 实例化具体后端。

密钥仍只进 `.env`（AGENTS.md：非 secret 不进 env 当用户文档入口）。

---

## 配置 → 工厂

```text
config.yaml  terminal.env_type / cwd / docker_* / ssh_* …
        │
        ▼  CLI / gateway 桥接
TERMINAL_ENV, TERMINAL_CWD, TERMINAL_DOCKER_IMAGE, …
        │
        ▼
_get_env_config()          # 解析、校验容器 cwd、组装 container_config
        │
        ▼
_create_environment(env_type, image, cwd, timeout, …)
        │
        ├─ local      → LocalEnvironment
        ├─ docker     → DockerEnvironment（可先 orphan reaper）
        ├─ singularity→ SingularityEnvironment
        ├─ modal      → ManagedModalEnvironment 或 ModalEnvironment
        ├─ daytona    → DaytonaEnvironment
        └─ ssh        → SSHEnvironment(host, user, port, key…)
```

打开摘录文件，重点看：

1. **`_get_env_config`**：`TERMINAL_ENV` 默认 `"local"`；container 后端才解析 CPU/memory JSON；docker 下 host cwd 能否挂到 `/workspace`。  
2. **`_create_environment`**：每个 `env_type` 分支构造参数；未知类型 `ValueError`。  

辅助：`env_probe.py` 用于探测当前后端能力（读 `TERMINAL_ENV`）。

---

## 与主循环的边界

| 层 | 是否知道 `TERMINAL_ENV` |
|----|-------------------------|
| `conversation_loop` | 通常否；只消费 tool JSON |
| `terminal_tool` | **是**；工厂 + env 复用 / 生命周期 |
| `BaseEnvironment` | 否；只实现 `execute` |

换后端 **不必** 改 system prompt / toolset → 保住 prompt cache。这是「能力放边缘、核心窄腰」的典型落点。

---

## 动手（真 Hermes，不是玩具）

1. 读 `hermes_src/tools/environments/__init__.py` + `terminal_tool.FACTORY.py`。  
2. 本机 Hermes：`terminal.env_type: local` 与 `docker`，同一条 terminal 命令对比输出。  
3. 断点建议：`_create_environment` 入口、`BaseEnvironment.execute`、`DockerEnvironment._run_bash`。

---

## 模块收束

1. **抽象**：`BaseEnvironment.execute` 统一。  
2. **多态**：`_run_bash` +（远程）`_before_execute`/file sync。  
3. **配置**：`TERMINAL_ENV` → factory；主循环无感。
