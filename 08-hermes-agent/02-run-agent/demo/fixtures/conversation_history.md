# 演示用对话历史（agent loop turn 之前）
#
# 格式对齐 01-memory/demo/fixtures/long_conversation.md：
#   ===== [i] role=... =====
#
# - system 行会被 loader 丢掉（真正的 system 由 MEMORY.md + USER.md 冻进缓存）
# - 场景：Julie 接着拆 Hermes 主循环，下一 turn 会要求 web_search

===== [0] role=system =====
## MEMORY
- 用户叫 Julie，在上海，想转 AI Agent Engineer
- 最近在拆 Hermes Agent 的 run_agent / conversation_loop

你是编程助手，回答要具体、能对着源码讲。

===== [1] role=user =====
Julie：我把 Memory / compress 看完了，接下来啃模块三主循环。`run_agent.py` 里搜不到 while，是不是循环搬走了？

===== [2] role=assistant =====
对。架构演变是：旧版 while 直接写在 `run_agent.py`；现在抽到 `agent/conversation_loop.py`，`AIAgent.run_conversation` 只剩 **forwarder**（方便测试 patch）。

面试一句：Runtime = 主循环 + 工具调度 + 状态 + 预算/中断。真正要断点的文件是 `conversation_loop`，不是 `run_agent` 的万行壳。

===== [3] role=user =====
那 while 条件我该背哪几个刹车？别跟我扯 gateway。

===== [4] role=assistant =====
三个（加 interrupt）：

1. **`max_iterations`**：硬上限（默认约 90）
2. **`IterationBudget.consume()`**：真正扣次数；`remaining` 是 while 预检
3. **`_budget_grace_call`**：预算用尽后再给 **一次** 收尾机会
4. **`_interrupt_requested`**：用户 /stop，下一圈 break

有 `tool_calls` → 执行 → append `role=tool` → continue；纯文本 → `final_response` 返回。

===== [5] role=user =====
todo 为什么还要 `registry.register`，执行却不走普通 dispatch？

===== [6] role=assistant =====
模式叫 **agent 级截胡**：

- schema 仍 register → 模型「看得见」todo
- 真正执行时 `invoke_tool` 先拦截 `todo` / `memory`，读写 `agent._todo_store`
- 结果仍以 JSON 字符串写回 `role=tool`

对比：`web_search` 这类普通工具走 `registry.dispatch`。Footprint 上 todo 进 core toolset，但状态留在 agent，不塞进通用 handler。

===== [7] role=user =====
好，下一轮我想对着真实网页/文档核对一遍 agent loop 说法。你会用工具的话，记得带上我们刚理的三个刹车。
