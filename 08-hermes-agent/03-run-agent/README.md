# Hermes Run Agent · 主循环如何学习

目标：讲清一次请求如何走完 **思考 → 调工具 → 观察 → 再思考**，以及预算 / 中断 / 工具发现。

对照大纲：[`../03-hermes Agent  学习大纲.md`](../03-hermes%20Agent%20%20学习大纲.md) **模块三**。

学法：

1. 读 `notes/` 讲稿（先建立心智模型）  
2. 打开 `hermes_src/` 按行号对照  
3. 真跑：完整 `hermes-agent/` 仓库里 `hermes` CLI 打断点看一轮 tool call  

> `hermes_src/` 只读剪枝，缺大量依赖，**import 跑不起来**。  
> 注意：当前上游已把循环抽到 `agent/conversation_loop.py`；`run_agent.py` 里的 `run_conversation` 只是 **forwarder**。

---

## 目录

```text
03-run-agent/
├── README.md
├── notes/
│   ├── 1_agent_loop.md          # while 循环 / 预算 / 中断
│   ├── 2_tools_discovery.md     # registry → model_tools → toolsets
│   └── 3_todo_intercept.md      # agent 级工具范例
└── hermes_src/
    ├── README.md
    ├── AGENTS.md                # Agent Loop + Footprint Ladder
    ├── run_agent.py             # AIAgent；run_conversation → forwarder
    ├── model_tools.py           # handle_function_call / get_tool_definitions
    ├── toolsets.py              # _HERMES_CORE_TOOLS / TOOLSETS
    ├── agent/
    │   └── conversation_loop.py # ★ 真正的 while 循环（~4k 行）
    └── tools/
        ├── registry.py          # discover_builtin_tools / register / dispatch
        └── todo_tool.py         # registry.register 范例 + 主循环拦截
```

关联（不在本目录，讲 prologue 时打开）：

- [`../04.1-memory/hermes_src/agent/turn_context.py`](../04.1-memory/hermes_src/agent/turn_context.py) — 每 turn 开场白  
- [`../04.1-memory/notebooks/7.turn_context.md`](../04.1-memory/notebooks/7.turn_context.md)

---

## 建议阅读顺序

| 顺序 | 材料 | 重点 |
|------|------|------|
| 1 | `notes/1_agent_loop.md` | 循环骨架 |
| 2 | `agent/conversation_loop.py` ~while | 真代码 |
| 3 | `run_agent.py` `run_conversation` forwarder | 架构演变 |
| 4 | `notes/2_tools_discovery.md` | 发现与分发 |
| 5 | `tools/registry.py` + `model_tools.py` | 行号对照 |
| 6 | `toolsets.py` `_HERMES_CORE_TOOLS` | narrow waist |
| 7 | `notes/3_todo_intercept.md` + `todo_tool.py` | agent 级工具 |

---

## 动手（对齐大纲产出）

1. 画主循环时序图：`system/user/assistant/tool` role 交替。  
2. CLI 打断点：停在 `conversation_loop` 的 while、以及 `handle_function_call`。  
3. 面试一句话：Runtime = 主循环 + 工具调度 + 状态 + 预算/中断；核心工具 schema 每次全量下发 → Footprint Ladder。

---

## 与其它模块

| 模块 | 关系 |
|------|------|
| [`04.1-memory/`](../04.1-memory/) | turn prologue、compress、cache |
| [`02-eval/`](../02-eval/) | 用 Trace 验证循环每一步 |
