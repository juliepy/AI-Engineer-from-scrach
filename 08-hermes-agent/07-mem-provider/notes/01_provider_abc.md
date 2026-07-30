# 01 · MemoryProvider ABC + MemoryManager

> 对照：  
> - [`../hermes_src/agent/memory_provider.py`](../hermes_src/agent/memory_provider.py)  
> - [`../hermes_src/agent/memory_manager.py`](../hermes_src/agent/memory_manager.py)  
> 下一篇：[`02_prefetch_and_inject.md`](./02_prefetch_and_inject.md)

---

## 一句话

Hermes 记忆分两层：**内置** `MemoryStore`（MEMORY.md / USER.md + `memory` 工具）和 **至多一个外部** `MemoryProvider`（Honcho / Mem0 / …）。`MemoryManager` 是唯一编排入口。

---

## 两条记忆轨

| 轨 | 存什么 | 进上下文的方式 |
|----|--------|----------------|
| **Builtin** | `~/.hermes/memories/MEMORY.md`、`USER.md` | Session 启动冻进 **system prompt volatile**；中途 `memory` 工具写盘 **不改** 当前 SP（保 cache） |
| **External Provider** | 各后端自己的库 | 静态说明 → `system_prompt_block()` 进 SP；动态召回 → `prefetch()` 进 **本轮 user message** |

`config.yaml` → `memory.provider` 选外部插件；未配则只有 builtin。

---

## Lifecycle（ABC 文件头）

```text
initialize()           — 连后端、暖机
system_prompt_block()  — 静态 SP 文本
prefetch(query)        — 本轮召回（要快，可返回缓存）
queue_prefetch(query)  — turn 结束后后台暖下一轮
sync_turn(user, asst)  — turn 结束后异步写入
get_tool_schemas()     — 可选 provider 工具
shutdown()
```

可选钩子：`on_turn_start` / `on_session_end` / `on_pre_compress` / `on_memory_write`（镜像 builtin 写入）等。

`initialize` 的 `agent_context`：`primary` / `subagent` / `cron` / `flush` —— **cron/subagent 应跳过写**，防污染用户表示。

---

## MemoryManager 硬规则

1. **只允许一个外部 provider**（再注册第二个直接 reject）。  
2. `prefetch_all` / `sync_all` 对每个 provider fail-open。  
3. `sync_all` / `queue_prefetch_all` 走 **后台线程**，不堵「用户已看到回复」的路径。  
4. Skill 展开消息会先 `_strip_skill_scaffolding`，只把用户真实指令喂给 provider。

下一篇：一轮对话里 **fetch 何时发生、怎样注入消息**。
