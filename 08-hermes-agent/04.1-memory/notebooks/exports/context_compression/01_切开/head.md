# head（protect head）

> = messages[:protect_first_n]。当前 protect_first_n=3，因此含 system + 首轮问答，**多于** system_prompt。

- 条数: 3
- roles: ['system', 'user', 'assistant']

===== [0] role=system =====
## MEMORY
- 用户叫 Julie，在上海，想转 AI Agent Engineer
- 主力 Python，做过 RAG Agent；最近在拆 Hermes Agent 源码

你是编程助手，回答要具体、能对着源码讲。

===== [1] role=user =====
我是 Julie，在上海准备转 AI Agent Engineer。今天卡在 Hermes 的 `context_compressor.py`：为什么对话一长就突然「改历史」了？我以为 Prompt Cache 绝对不能动过去的 messages。

===== [2] role=assistant =====
Julie，你的直觉大体对：Hermes 平时确实不改历史，为的是保住 per-conversation 的 prompt cache。

唯一例外就是 context compression。触发条件大致是：当前 messages 的粗估 token 越过 `context_length * threshold_percent`。一旦触发，不会整段删掉，而是切开：

1. **protect head**：通常保住 system（含你 MEMORY 里「Julie / 上海 / AI Engineer」）和前几轮
2. **middle**：中间轮次序列化成文本，丢给辅助模型做结构化摘要
3. **protect tail**：最近几轮原样留下，因为还在接着干

所以「改历史」不是乱改，而是把 middle 换成一条带 `SUMMARY_PREFIX` 的摘要消息。Cache 会被这一刀打断——这是刻意权衡：爆窗比多花一点 cache 更糟。
