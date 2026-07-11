# 多通道检索架构说明

## 概述

本项目实现了一个可扩展的多通道检索架构，支持：
- **多种检索策略**：向量全局检索、意图定向检索、ES 关键词检索等
- **灵活的后置处理**：去重、版本过滤、分数归一化、Rerank 等
- **易于扩展**：新增检索通道或后置处理器只需实现接口并注册为 Spring Bean

## 架构设计

```
用户问题
    ↓
【问题重写】
    ↓
【多通道并行检索】
    ├─→ VectorGlobalSearchChannel（向量全局检索）
    ├─→ IntentDirectedSearchChannel（意图定向检索）
    └─→ KeywordESSearchChannel（ES 关键词检索，未来扩展）
    ↓
【结果聚合】
    ↓
【后置处理器链】
    ├─→ DeduplicationPostProcessor（去重）
    ├─→ VersionFilterPostProcessor（版本过滤）
    ├─→ ScoreNormalizationPostProcessor（分数归一化）
    └─→ RerankPostProcessor（重排序）
    ↓
【上下文格式化】
    ↓
【LLM 生成答案】
```

## 核心组件

### 1. 检索通道（SearchChannel）

检索通道负责执行具体的检索策略。

**接口定义**：
```java
public interface SearchChannel {
    String getName();                              // 通道名称
    int getPriority();                             // 优先级
    boolean isEnabled(SearchContext context);      // 是否启用
    SearchChannelResult search(SearchContext context);  // 执行检索
    SearchChannelType getType();                   // 通道类型
}
```

**已实现的通道**：
- `VectorGlobalSearchChannel`：向量全局检索，在所有知识库中检索
- `IntentDirectedSearchChannel`：意图定向检索，基于意图识别结果在特定知识库中检索

**扩展示例**：
```java
@Component
public class KeywordESSearchChannel implements SearchChannel {
    @Override
    public String getName() {
        return "KeywordESSearch";
    }

    @Override
    public boolean isEnabled(SearchContext context) {
        // 判断是否启用该通道
        return containsKeywords(context.getMainQuestion());
    }

    @Override
    public SearchChannelResult search(SearchContext context) {
        // 实现 ES 检索逻辑
        // ...
    }
}
```

### 2. 后置处理器（SearchResultPostProcessor）

后置处理器对检索结果进行统一的后处理。

**接口定义**：
```java
public interface SearchResultPostProcessor {
    String getName();                              // 处理器名称
    int getOrder();                                // 执行顺序
    boolean isEnabled(SearchContext context);      // 是否启用
    List<RetrievedChunk> process(                  // 处理结果
        List<RetrievedChunk> chunks,
        List<SearchChannelResult> results,
        SearchContext context
    );
}
```

**已实现的处理器**：
- `DeduplicationPostProcessor`：去重，合并多个通道的结果
- `RerankPostProcessor`：重排序，使用 Rerank 模型对结果进行精排

**扩展示例**：
```java
@Component
public class VersionFilterPostProcessor implements SearchResultPostProcessor {
    @Override
    public String getName() {
        return "VersionFilter";
    }

    @Override
    public int getOrder() {
        return 2;  // 在去重之后执行
    }

    @Override
    public List<RetrievedChunk> process(
        List<RetrievedChunk> chunks,
        List<SearchChannelResult> results,
        SearchContext context
    ) {
        // 实现版本过滤逻辑
        // 当检索到同一文档的多个版本时，只保留最新版本
        // ...
    }
}
```

### 3. 多通道检索引擎（MultiChannelRetrievalEngine）

协调多个检索通道和后置处理器的执行。

**核心方法**：
```java
public List<RetrievedChunk> retrieveKB(List<SubQuestionIntent> subIntents, int topK) {
    // 1. 构建检索上下文
    SearchContext context = buildSearchContext(subIntents, topK);

    // 2. 并行执行所有启用的检索通道
    List<SearchChannelResult> channelResults = executeSearchChannels(context);

    // 3. 依次执行后置处理器链
    List<RetrievedChunk> processedChunks = executePostProcessors(channelResults, context);

    return processedChunks;
}
```

## 配置说明

配置文件：`application-search.yml`

```yaml
rag:
  search:
    channels:
      vector-global:
        enabled: true
        confidence-threshold: 0.6  # 意图置信度低于此值时启用
        top-k-multiplier: 3

      intent-directed:
        enabled: true
        min-intent-score: 0.4
        top-k-multiplier: 2

    post-processors:
      deduplication:
        enabled: true
      rerank:
        enabled: true
```

## 使用示例

### 1. 基本使用

```java
@Service
public class RAGService {
    @Autowired
    private MultiChannelRetrievalEngine retrievalEngine;

    public void search(String question) {
        // 构建意图列表
        List<SubQuestionIntent> intents = ...;

        // 执行多通道检索
        List<RetrievedChunk> chunks = retrievalEngine.retrieveKB(intents, 5);

        // 使用检索结果
        // ...
    }
}
```

### 2. 新增检索通道

```java
@Component
public class CustomSearchChannel implements SearchChannel {
    @Override
    public String getName() {
        return "CustomSearch";
    }

    @Override
    public int getPriority() {
        return 5;  // 中等优先级
    }

    @Override
    public boolean isEnabled(SearchContext context) {
        // 自定义启用条件
        return true;
    }

    @Override
    public SearchChannelResult search(SearchContext context) {
        // 实现自定义检索逻辑
        List<RetrievedChunk> chunks = ...;

        return SearchChannelResult.builder()
            .channelType(SearchChannelType.HYBRID)
            .channelName(getName())
            .chunks(chunks)
            .confidence(0.8)
            .build();
    }

    @Override
    public SearchChannelType getType() {
        return SearchChannelType.HYBRID;
    }
}
```

### 3. 新增后置处理器

```java
@Component
public class CustomPostProcessor implements SearchResultPostProcessor {
    @Override
    public String getName() {
        return "CustomProcessor";
    }

    @Override
    public int getOrder() {
        return 5;  // 在去重之后、Rerank 之前执行
    }

    @Override
    public boolean isEnabled(SearchContext context) {
        return true;
    }

    @Override
    public List<RetrievedChunk> process(
        List<RetrievedChunk> chunks,
        List<SearchChannelResult> results,
        SearchContext context
    ) {
        // 实现自定义处理逻辑
        // 例如：过滤、排序、增强等
        return chunks.stream()
            .filter(chunk -> chunk.getScore() > 0.5)
            .toList();
    }
}
```

## 工作流程

### 1. 检索通道执行

所有启用的检索通道会**并行执行**，互不影响：

```
VectorGlobalSearchChannel  ─┐
                            ├─→ 并行执行
IntentDirectedSearchChannel ─┘
```

每个通道返回 `SearchChannelResult`，包含：
- 检索到的 Chunk 列表
- 通道置信度
- 检索耗时
- 元数据

### 2. 后置处理器链执行

后置处理器按照 `order` 顺序**依次执行**，形成处理链：

```
原始 Chunks
    ↓
DeduplicationPostProcessor (order=1)
    ↓
VersionFilterPostProcessor (order=2)
    ↓
RerankPostProcessor (order=10)
    ↓
最终 Chunks
```

## 扩展点

### 1. 新增检索通道类型

在 `SearchChannelType` 枚举中添加新类型：

```java
public enum SearchChannelType {
    VECTOR_GLOBAL,
    INTENT_DIRECTED,
    KEYWORD_ES,
    HYBRID,
    CUSTOM_TYPE  // 新增类型
}
```

### 2. 自定义通道启用条件

在 `isEnabled` 方法中实现自定义逻辑：

```java
@Override
public boolean isEnabled(SearchContext context) {
    // 示例：只在问题包含特定关键词时启用
    String question = context.getMainQuestion();
    return question.contains("实时") || question.contains("最新");
}
```

### 3. 自定义后置处理逻辑

实现 `SearchResultPostProcessor` 接口，添加自定义处理逻辑：

```java
@Component
public class ScoreBoostPostProcessor implements SearchResultPostProcessor {
    @Override
    public List<RetrievedChunk> process(...) {
        // 示例：对特定来源的 Chunk 提升分数
        return chunks.stream()
            .map(chunk -> {
                if (isHighQualitySource(chunk)) {
                    chunk.setScore(chunk.getScore() * 1.2f);
                }
                return chunk;
            })
            .toList();
    }
}
```

## 优势

1. **高覆盖率**：多通道并行检索，即使意图识别失败也能通过全局检索兜底
2. **高准确率**：意图定向检索提供精确结果，Rerank 进一步优化排序
3. **易扩展**：新增通道或处理器只需实现接口，无需修改核心代码
4. **灵活配置**：通过配置文件控制通道和处理器的启用状态
5. **性能优化**：通道并行执行，处理器按需启用

## 注意事项

1. **通道优先级**：数字越小优先级越高，影响去重时的结果保留策略
2. **处理器顺序**：`order` 决定执行顺序，去重应该最先执行，Rerank 应该最后执行
3. **性能考虑**：启用过多通道会增加延迟，建议根据实际需求选择性启用
4. **配置调优**：`confidence-threshold`、`top-k-multiplier` 等参数需要根据实际效果调整

## 未来扩展

1. **ES 关键词检索通道**：基于 Elasticsearch 的全文检索
2. **版本过滤处理器**：当检索到同一文档的多个版本时，只保留最新版本
3. **分数归一化处理器**：统一不同通道的分数尺度
4. **缓存机制**：对检索结果进行缓存，提升性能
5. **监控和统计**：记录各通道的命中率、耗时等指标
