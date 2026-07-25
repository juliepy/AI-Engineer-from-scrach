# Agent Loop Demo

可跑通的 **思考 → 调工具 → 观察 → 再思考** 主循环，打印：

1. MEMORY / USER 冻进 system（对齐 `01-memory`）
2. `conversation_history.md` 作为本 turn 之前的 messages
3. `todo`（agent 截胡）+ `web_search`（registry / 真搜索）
4. while 每一步 API + budget + role 时序

## 目录

```text
demo/
├── README.md
├── run_agent_loop.py
├── requirements.txt
├── fixtures/
│   ├── MEMORY.md                 # 同 01-memory
│   ├── USER.md                   # 同 01-memory
│   └── conversation_history.md   # 本 turn 之前的对话（agent loop 话题）
├── teaching/
│   ├── agent_loop/               # ← notes/1
│   │   ├── agent.py
│   │   ├── conversation_loop.py  # ★ while
│   │   ├── iteration_budget.py
│   │   └── llm.py                # DeepSeek + tools
│   ├── tools/                    # ← notes/2
│   │   ├── registry.py
│   │   └── web_search_tool.py    # 对照 web_tools.py schema/返回形
│   ├── todo/                     # ← notes/3
│   │   ├── invoke_tool.py        # todo 截胡
│   │   └── todo_tool.py
│   └── memory/                   # 同 01-memory
│       └── teaching_memory.py
└── exports/agent_loop/
```

对照：

| 本 demo | 源码 / 其它模块 |
|---------|-----------------|
| `agent_loop/conversation_loop.py` | `agent/conversation_loop.py` while |
| `todo/todo_tool.py` + `invoke_tool` | `tools/todo_tool.py` + agent 级截胡 |
| `tools/web_search_tool.py` | `tools/web_tools.py`（schema + `{success,data.web}`） |
| `memory/teaching_memory.py` + fixtures | `01-memory/demo` |

---

## Code Call Flow

```text
run_agent_loop.main()
 │
 ├─① TeachingMemoryStore.load_from_disk(MEMORY.md, USER.md)
 │      → frozen system_prompt (+ tools guidance)
 │
 ├─② load_conversation_history(conversation_history.md)
 │      → 丢掉内嵌 system；保留 user/assistant
 │
 ├─③ registry: todo + web_search
 │      web backend: Tavily(若有 key) → ddgs → DuckDuckGo Instant
 │
 └─④ DemoAgent.run_conversation(user, history, system)
        └─ while: DeepSeek → tool_calls? → invoke → continue
```

---

## 跑法

```powershell
cd 02-run-agent/demo
pip install -r requirements.txt
python run_agent_loop.py
```

```env
DEEPSEEK_API_KEY=sk-...
# 可选：有则优先走 Tavily（更稳）；否则用 ddgs
TAVILY_API_KEY=tvly-...
```

---

## 产物

```text
exports/agent_loop/
├── 00_workflow.md
├── 00_memory_block.md / 00_user_block.md
├── 01_system.md
├── 02_user.md / 02_history.md
├── 03_tools_schema.json
├── 04_messages.md
├── 05_final_response.md
├── 06_trace.md
└── 07_todo_store.json
```
