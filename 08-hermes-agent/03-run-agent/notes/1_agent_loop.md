# 1 · Agent Loop：思考 → 工具 → 观察

> 对照：`../hermes_src/agent/conversation_loop.py`（`run_conversation` ~`:228`，while ~`:639`）  
> Forwarder：`../hermes_src/run_agent.py` ~`:5787`  
> Prologue：`../../04.1-memory/hermes_src/agent/turn_context.py`

---

## 0. 一句话

一次用户消息进入 `run_conversation` 后：先做 turn prologue，再进入 **同步 while**：调模型 → 若有 `tool_calls` 则执行并写回 messages → 再调模型；直到无工具、触顶预算、或 interrupt。

---

## 1. 两层结构（先画图）

```text
AIAgent.run_conversation(...)          # run_agent.py · 薄转发
        │
        ▼
agent.conversation_loop.run_conversation(agent, ...)
        │
        ├─ build_turn_context / 等价 prologue   # 拼 messages、system、预压缩…
        │
        └─ while 循环                           # ★ 本讲核心
              ├─ API call (interruptible)
              ├─ tool_calls? → _execute_tool_calls → 继续
              └─ 纯文本? → 收尾返回
```

架构演变（面试加分）：

> 旧：`run_agent.py` 上万行扛一切。  
> 新：循环抽到 `conversation_loop.py`；`run_agent.AIAgent.run_conversation` 只剩 forwarder，方便测试 patch 兼容。

---

## 2. 循环骨架（AGENTS.md 示意 = 真代码浓缩）

```python
while (api_call_count < agent.max_iterations and agent.iteration_budget.remaining > 0) \
        or agent._budget_grace_call:
    if agent._interrupt_requested:
        break
    # consume budget / grace call 处理…
    response = client.chat.completions.create(..., messages=..., tools=...)
    if response.tool_calls:
        execute tools → append role=tool messages
        api_call_count += 1
        continue
    else:
        return final_response
```

真文件定位：

| 关注点 | 约行号（conversation_loop.py） |
|--------|--------------------------------|
| `def run_conversation` | 228 |
| while 条件 | 639 |
| `_interrupt_requested` 检查 | while 内靠前 |
| `iteration_budget.consume` / grace | while 入口附近 |
| 处理 `assistant_message.tool_calls` | ~3199+ |
| `_execute_tool_calls` | ~3430 |

---

## 3. 三个刹车（防死循环）

| 机制 | 作用 |
|------|------|
| `max_iterations` | 硬上限（默认约 90，与 subagent 共享语义） |
| `IterationBudget` | 可 consume / refund（部分 housekeeping 工具可退回） |
| `_budget_grace_call` | 预算用尽后 **再给一次** 收尾机会 |
| `_interrupt_requested` | 用户 /stop；工具级也可取消 |

---

## 4. 消息 role 交替（时序图作业）

```text
system          （cached，会话内稳定）
user            （本 turn）
assistant       （可能含 tool_calls）
tool            （结果，可多条）
assistant
…
assistant       （最终纯文本）
```

铁律（与 Cache 章一致）：**不要**中途插入合成 user、不要连着两条同 role（严格模板会炸）；压缩是改历史的例外。

---

## 5. 和 turn_context 的分工

| | turn_context | conversation_loop |
|--|--------------|-------------------|
| 何时 | 每 turn **一次** prologue | prologue 之后的 **多轮** API |
| 产出 | `TurnContext` | `final_response` + messages |
| 压缩 | preflight 压缩 | overflow 路径上可能再压 |

---

## 6. 建议讲解（15–20 min）

1. Forwarder vs 真循环（打开两个文件各 10 秒）  
2. while 条件三要素：iterations / budget / grace  
3. tool_calls 分支 vs 文本分支  
4. 画 role 时序  
5. 留作业：在完整仓库对 while 打断点  

---

## 7. 自检

1. 为什么在 `run_agent.py` 里搜不到 while 循环？  
2. grace call 解决什么体验问题？  
3. 有 tool_calls 时 messages 里最少会新增哪两种 role？
