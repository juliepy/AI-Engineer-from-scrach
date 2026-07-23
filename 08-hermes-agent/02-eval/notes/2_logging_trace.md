# 2 · Logging / Trace：从日志追因果

> 对照：`../hermes_src/hermes_logging.py`  
> 命令：完整仓库里 `hermes logs [--follow] [--session ...] [--component ...]`

---

## 0. 一句话

Hermes 把可观测性落在 **分文件结构化日志 + 每条记录带 `session_tag`**。Trace 分析 = 用同一个 `session_id` 把 LLM / tool / gateway 事件串成因果链。

---

## 1. 文件地图

| 行号（约） | 符号 | 讲什么 |
|-----------|------|--------|
| 165 | `set_session_context` | turn 开始打上 session_id |
| 183 | `_install_session_record_factory` | 每条 LogRecord 注入 `session_tag` |
| 236 | `COMPONENT_PREFIXES` | gateway / agent / tools / cli / … |
| 259 | `setup_logging` | 主入口：轮转 + 脱敏 + 分流 |
| 647+ | `flush_log_queue` / `drain_log_queue` | 测试 vs 退出时排空 |

日志文件（`~/.hermes/logs/`，profile-aware）：

| 文件 | 内容 |
|------|------|
| `agent.log` | INFO+ 主路径 |
| `errors.log` | WARNING+ |
| `gateway.log` | 消息网关 |

---

## 2. 为什么要 `session_tag`

```text
多会话并发（gateway / 多 profile）
        │
        ▼
每条日志带 [session_abc123]
        │
        ▼
hermes logs --session abc123  → 只看这一条对话的因果
```

`turn_context.build_turn_context` 里会调 `set_session_context(agent.session_id)`——和主循环模块衔接。

---

## 3. Trace 概念对照（面试用）

| 概念 | 在 Hermes 里常落在 |
|------|-------------------|
| trace_id | 粗对齐：`session_id`（+ turn_id） |
| span | 一次 API call / 一次 tool 执行（看 agent.log 时间序） |
| Metrics | 成本、步数、压缩次数（可外接 LangFuse） |
| Log | 细节与异常栈 |

根因三问（对着一条完整 Trace）：

1. **工具选错？** → 看 assistant `tool_calls` 名 vs 任务  
2. **上下文溢出？** → 搜 compression / preflight / context length  
3. **预算耗尽？** → 搜 `Iteration budget exhausted` / `max_iterations`

---

## 4. 建议讲解顺序（10 min）

1. `setup_logging` 产出哪些文件  
2. `COMPONENT_PREFIXES` 为什么要分流  
3. `set_session_context` → 格式串里的 `%(session_tag)s`  
4. 现场假想一条失败：从 gateway 进 → agent 调 tool → errors.log  

---

## 5. 自检

1. `agent.log` 和 `gateway.log` 怎么分流？  
2. 没有 `session_tag` 时排查多会话问题会怎样？  
3. Trace / Metrics / Log 三者各回答什么问题？
