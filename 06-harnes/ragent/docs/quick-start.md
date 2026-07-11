# 快速开始指南

## 重构完成的内容

本次重构实现了一个**多通道检索 + 后置处理器**的可扩展架构，解决了意图识别覆盖率不足的问题。

## 新增的文件

### 1. 核心接口（`channel` 包）
```
bootstrap/src/main/java/com/nageoffer/ai/ragent/rag/core/retrieve/channel/
├── SearchChannel.java              # 检索通道接口
├── SearchChannelType.java          # 通道类型枚举
├── SearchContext.java              # 检索上下文
└── SearchChannelResult.java        # 通道结果
```

### 2. 检索通道实现（`channel/impl` 包）
```
bootstrap/src/main/java/com/nageoffer/ai/ragent/rag/core/retrieve/channel/impl/
├── VectorGlobalSearchChannel.java      # 向量全局检索
└── IntentDirectedSearchChannel.java    # 意图定向检索
```

### 3. 后置处理器（`postprocessor` 包）
```
bootstrap/src/main/java/com/nageoffer/ai/ragent/rag/core/retrieve/postprocessor/
├── SearchResultPostProcessor.java      # 后置处理器接口
└── impl/
    ├── DeduplicationPostProcessor.java # 去重处理器
    └── RerankPostProcessor.java        # Rerank 处理器
```

### 4. 多通道检索引擎
```
bootstrap/src/main/java/com/nageoffer/ai/ragent/rag/core/retrieve/
└── MultiChannelRetrievalEngine.java    # 多通道检索引擎
```

### 5. 配置和文档
```
bootstrap/src/main/resources/
└── application-search.yml              # 检索配置

docs/
├── multi-channel-retrieval.md          # 架构说明文档
├── refactoring-summary.md              # 重构总结
└── quick-start.md                      # 本文档
```

## 工作原理

### 1. 检索流程

```
用户问题
    ↓
【意图识别】
    ↓
【多通道并行检索】
    ├─→ 意图定向检索（始终执行）
    └─→ 向量全局检索（条件触发：意图置信度 < 0.6）
    ↓
【后置处理器链】
    ├─→ 去重（合并多通道结果）
    └─→ Rerank（重排序）
    ↓
【返回 Top-K 结果】
```

### 2. 条件触发逻辑

**向量全局检索**在以下情况下启用：
- 没有识别出任何意图
- 意图置信度都很低（< 0.6）

这样既保证了覆盖率，又避免了不必要的性能开销。

## 如何使用

### 1. 现有代码无需修改

`RetrievalEngine` 已经集成了多通道检索引擎，现有的调用代码无需修改：

```java
// 原有代码继续工作
RetrievalContext context = retrievalEngine.retrieve(subIntents, topK);
```

### 2. 配置调整（可选）

如果需要调整检索策略，修改 `application.yaml`：

```yaml
rag:
  search:
    channels:
      vector-global:
        enabled: true
        confidence-threshold: 0.6  # 调整触发阈值
        top-k-multiplier: 3        # 调整召回倍数
      intent-directed:
        enabled: true
        min-intent-score: 0.4      # 最低意图分数
        top-k-multiplier: 2        # 调整召回倍数
```

**配置说明**：
- `enabled`: 是否启用该检索通道
- `confidence-threshold`: 意图置信度阈值，低于此值时启用全局检索
- `top-k-multiplier`: TopK 倍数，控制召回的候选数量
- `min-intent-score`: 最低意图分数，低于此分数的意图节点会被过滤

**注意**：后置处理器（去重、Rerank）是代码层面的逻辑，不需要配置文件控制。如果需要新增或修改后置处理器，直接实现 `SearchResultPostProcessor` 接口即可。

### 3. 查看日志

启动应用后，可以在日志中看到检索通道的执行情况：

```
INFO  启用的检索通道：[IntentDirectedSearch, VectorGlobalSearch]
INFO  执行检索通道：IntentDirectedSearch
INFO  执行检索通道：VectorGlobalSearch
INFO  通道 IntentDirectedSearch 完成，检索到 15 个 Chunk，置信度：0.85，耗时：120ms
INFO  通道 VectorGlobalSearch 完成，检索到 20 个 Chunk，置信度：0.7，耗时：150ms
INFO  启用的后置处理器：[Deduplication, Rerank]
INFO  执行后置处理器：Deduplication
INFO  去重完成，输入 Chunk 数：35，输出 Chunk 数：28
INFO  执行后置处理器：Rerank
INFO  Rerank 完成，输出 Chunk 数：5
```

## 扩展示例

### 1. 新增 ES 关键词检索通道

```java
@Component
public class KeywordESSearchChannel implements SearchChannel {

    @Autowired
    private ElasticsearchClient esClient;

    @Override
    public String getName() {
        return "KeywordESSearch";
    }

    @Override
    public int getPriority() {
        return 5;  // 中等优先级
    }

    @Override
    public boolean isEnabled(SearchContext context) {
        // 当问题包含专有名词或代码片段时启用
        String question = context.getMainQuestion();
        return containsCode(question) || containsProperNouns(question);
    }

    @Override
    public SearchChannelResult search(SearchContext context) {
        // 实现 ES 检索逻辑
        List<RetrievedChunk> chunks = searchByKeywords(
            context.getMainQuestion(),
            context.getTopK() * 2
        );

        return SearchChannelResult.builder()
            .channelType(SearchChannelType.KEYWORD_ES)
            .channelName(getName())
            .chunks(chunks)
            .confidence(0.8)
            .build();
    }

    @Override
    public SearchChannelType getType() {
        return SearchChannelType.KEYWORD_ES;
    }

    private boolean containsCode(String question) {
        // 判断是否包含代码片段
        return question.contains("```") || question.matches(".*\\b(class|function|def|import)\\b.*");
    }

    private boolean containsProperNouns(String question) {
        // 判断是否包含专有名词（大写开头的词）
        return question.matches(".*\\b[A-Z][a-z]+\\b.*");
    }
}
```

### 2. 新增版本过滤处理器

```java
@Component
public class VersionFilterPostProcessor implements SearchResultPostProcessor {

    @Override
    public String getName() {
        return "VersionFilter";
    }

    @Override
    public int getOrder() {
        return 2;  // 在去重之后、Rerank 之前执行
    }

    @Override
    public boolean isEnabled(SearchContext context) {
        // 可以通过配置或上下文判断是否启用
        return true;
    }

    @Override
    public List<RetrievedChunk> process(List<RetrievedChunk> chunks,
                                         List<SearchChannelResult> results,
                                         SearchContext context) {
        // 按文档 ID 分组
        Map<String, List<RetrievedChunk>> docGroups = chunks.stream()
            .collect(Collectors.groupingBy(this::extractDocumentId));

        List<RetrievedChunk> filtered = new ArrayList<>();

        for (Map.Entry<String, List<RetrievedChunk>> entry : docGroups.entrySet()) {
            List<RetrievedChunk> versions = entry.getValue();

            if (versions.size() == 1) {
                filtered.addAll(versions);
            } else {
                // 保留最新版本
                RetrievedChunk latest = versions.stream()
                    .max(Comparator.comparing(this::extractVersion))
                    .orElse(versions.get(0));
                filtered.add(latest);
            }
        }

        return filtered;
    }

    private String extractDocumentId(RetrievedChunk chunk) {
        // 从 chunk ID 中提取文档 ID
        String chunkId = chunk.getId();
        if (chunkId != null && chunkId.contains(":")) {
            return chunkId.substring(0, chunkId.lastIndexOf(":"));
        }
        return chunkId;
    }

    private String extractVersion(RetrievedChunk chunk) {
        // 从 chunk ID 中提取版本号
        String chunkId = chunk.getId();
        if (chunkId != null && chunkId.contains(":")) {
            return chunkId.substring(chunkId.lastIndexOf(":") + 1);
        }
        return "0";
    }
}
```

## 测试建议

### 1. 测试意图识别成功的场景

```java
// 问题：OA系统如何保证数据安全？
// 预期：只执行意图定向检索，不触发全局检索
```

### 2. 测试意图识别失败的场景

```java
// 问题：如何提升系统性能？（没有明确的意图）
// 预期：同时执行意图定向检索和全局检索
```

### 3. 测试去重效果

```java
// 预期：同一个 Chunk 在多个通道中出现时，只保留一份
```

### 4. 测试 Rerank 效果

```java
// 预期：最终返回的 Top-K 结果是经过 Rerank 优化的
```

## 性能优化建议

1. **调整触发阈值**：根据实际效果调整 `confidence-threshold`
2. **调整召回倍数**：根据 Rerank 效果调整 `top-k-multiplier`
3. **选择性启用通道**：根据实际需求启用或禁用特定通道
4. **监控性能指标**：记录各通道的耗时和命中率

## 常见问题

### Q1: 为什么有时候会执行两次检索？

A: 当意图识别置信度低于阈值（默认 0.6）时，会同时执行意图定向检索和全局检索，以保证覆盖率。

### Q2: 如何禁用全局检索？

A: 在 `application.yaml` 中设置：
```yaml
rag:
  search:
    channels:
      vector-global:
        enabled: false
```

### Q3: 如何调整意图识别的触发阈值？

A: 在 `application.yaml` 中设置：
```yaml
rag:
  search:
    channels:
      vector-global:
        confidence-threshold: 0.7  # 提高阈值，减少全局检索触发
```

### Q4: 如何新增自定义的检索通道？

A: 实现 `SearchChannel` 接口，并注册为 Spring Bean（使用 `@Component` 注解）。

### Q5: 如何新增自定义的后置处理器？

A: 实现 `SearchResultPostProcessor` 接口，并注册为 Spring Bean（使用 `@Component` 注解）。

## 下一步

1. **运行应用**：启动应用，观察日志中的检索流程
2. **测试效果**：对比重构前后的检索覆盖率和准确率
3. **调优配置**：根据实际效果调整配置参数
4. **扩展功能**：根据需求新增检索通道或后置处理器

## 参考文档

- [架构说明文档](./multi-channel-retrieval.md)
- [重构总结](./refactoring-summary.md)

## 联系方式

如有问题，请查看详细的架构说明文档或联系开发团队。
