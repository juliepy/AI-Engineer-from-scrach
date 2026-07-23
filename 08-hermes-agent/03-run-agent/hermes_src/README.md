# hermes_src · Run Agent 只读对照

从 `hermes-study/` + 上游 `agent/conversation_loop.py` 剪出，**不是可运行工程**。

| 文件 | 职责 |
|------|------|
| `run_agent.py` | `AIAgent` 类；`run_conversation` **转发**到 conversation_loop |
| `agent/conversation_loop.py` | ★ 真正的工具循环（while + 预算 + 中断 + tool 分发） |
| `model_tools.py` | `get_tool_definitions` / `handle_function_call` |
| `toolsets.py` | `_HERMES_CORE_TOOLS`、按平台 `TOOLSETS` |
| `tools/registry.py` | `discover_builtin_tools`、`register`、`dispatch` |
| `tools/todo_tool.py` | 自注册工具范例；常被主循环提前拦截 |
| `AGENTS.md` | Agent Loop 示意 + Footprint Ladder |

依赖链（先读这个）：

```text
tools/registry.py
      ↑
tools/*.py  (import 时 register)
      ↑
model_tools.py  (触发 discover)
      ↑
conversation_loop / run_agent
```
