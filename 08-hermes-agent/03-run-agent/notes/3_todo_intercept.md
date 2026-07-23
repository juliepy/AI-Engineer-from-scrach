# 3 · Todo：agent 级工具拦截范例

> 对照：`../hermes_src/tools/todo_tool.py`  
> 主循环里常在 `handle_function_call` **之前**接管（见 AGENTS.md「Agent-level tools」）

---

## 0. 一句话

多数工具：registry 分发即可。  
少数工具（`todo`、`memory`）：与 **会话状态紧耦合**，由 `AIAgent` / 循环提前拦截，避免走通用路径丢状态。

---

## 1. 看什么

| 位置 | 内容 |
|------|------|
| `todo_tool.py` 业务函数 | 增删改查 todo 列表 |
| 文件末尾 `registry.register` | 仍注册 schema，让模型「看见」工具 |
| 主循环拦截点 | 真正执行时走 agent 持有的 `_todo_store` |

模式：

```text
模型以为在调普通 tool
        │
        ▼
schema 来自 registry（可见）
        │
        ▼
执行被 AIAgent 截胡 → 读写 agent 内存态
        │
        ▼
仍以 JSON 字符串结果写回 role=tool
```

---

## 2. 和 Footprint 的关系

- Todo 是「几乎人人需要」的会话规划能力 → 可进 core toolset。  
- 但仍保持 **窄实现**：状态在 agent，不把复杂存储塞进通用 handler。

---

## 3. 自检

1. 为什么 todo 还要 `registry.register`？  
2. 若只 register 不拦截，会出什么问题？
