从 `TurnContext.preflight()` 视角看，压缩就像“在每次给主模型发消息之前，检查一下上下文会不会撑爆，如果会，就当场瘦身”。

### 1. 什么时候触发（`preflight()` 检查逻辑）
在 `TurnContext.preflight()` 里，大致流程是：
1. 计算当前要发给主模型的全量消息（`messages_for_completion()`）的 token 数。
2. 拿这个 token 数和当前模型的 `context_length * threshold_percent`（如 0.8）做比较。
3. **如果 token 数 > 阈值** 就触发压缩，调用 `ContextCompressor.compress()`；否则直接跳过。

所以触发条件就是**粗估累计消息过长，快超出模型窗口**。注意阈值可配置，并不是等到 100% 才压，给压缩本身和后续生成留空余量。

---

### 2. 压缩后发给主模型的 messages 长什么样（最终产出）
压缩完成后，`preflight()` 重新调用 `messages_for_completion()` 组装最终消息。压缩后的 messages 结构（以 `protect_first_n=1, protect_last_n=2` 为例）：

```
[ system (原始 system prompt，包含 MEMORY) ]
[ user (摘要消息，以 SUMMARY_PREFIX 开头) ]
[ ... tail 里倒数第 2 条消息 ... ]
[ ... tail 里倒数第 1 条消息（最新） ]
```

**关键细节：**

- **head（保护头部）**：原始 `protect_first_n` 条不动，通常至少包含 system prompt + MEMORY，保证角色设定和关键记忆不丢。
- **middle（被压缩部分）**：head 和 tail 之间的所有消息，被送给辅助模型生成**结构化摘要**。摘要内容会附上 `SUMMARY_PREFIX`（例如 `[CONTEXT COMPACTION — REFERENCE ONLY]`），然后打包成一条 **role = "user"** 的消息插回。
  - role 选 `user` 有深意：既避免摘要被当成 assistant 的话产生连贯幻觉，又防止摘要混入 system 指令执行操作。
  - `SUMMARY_PREFIX` 明确声明“只读背景，不要重答旧任务”，并且摘要模板里用的是历史归档语气（`Historical Task`、`Pending Asks`、`Remaining Work`），进一步封印摘要模型的能动性。
- **tail（保护尾部）**：最近 `protect_last_n` 条消息原样保留，保证当前在进行的对话不被打断。
- **MEMORY 的去向**：通常在 head 的 system 里原样保留。如果怕摘要丢失关键事实，`MemoryProvider.on_pre_compress()` 会把“重点结论”作为 `provider_hint` 插入压缩提示，让摘要至少照顾到。

所以，主模型最终拿到的是一个**头部不变、中部被概括为一则用户消息、尾部最近消息完整的混合消息列表**。代价是 prompt cache 在压缩点被打断，但换来了上下文不爆窗、对话能继续。