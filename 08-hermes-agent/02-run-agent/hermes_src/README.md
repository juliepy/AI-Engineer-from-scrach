# hermes_src — Agent Loop 对照剪枝

本目录只读，方便对照 `demo/teaching/`。完整循环在上游约 4k 行，这里放：

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | Agent Loop 示意 + Footprint Ladder |
| `agent/iteration_budget.py` | 预算 consume / refund（原样） |
| `agent/conversation_loop.SKELETON.md` | while 骨架摘录（讲解用） |
| `tools/registry.py` | register / discover / dispatch |
| `tools/todo_tool.py` | TodoStore + registry.register 范例 |

真跑请用 `../demo/`（DeepSeek）。上游完整文件：

- https://github.com/NousResearch/hermes-agent/blob/main/agent/conversation_loop.py
- https://github.com/NousResearch/hermes-agent/blob/main/agent/agent_runtime_helpers.py
