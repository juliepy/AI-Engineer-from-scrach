# 重构总结

## 重构目标

实现一个可扩展的多通道检索架构，解决以下问题：
1. **意图识别覆盖率不足**：当文档内容较多时，意图识别树的示例问题无法覆盖所有场景
2. **缺乏兜底机制**：意图识别失败时，无法检索到相关文档
3. **扩展性差**：新增检索策略需要修改核心代码

## 重构内容

### 1. 新增文件

#### 核心接口和类型
- `SearchChannel.java` - 检索通道接口
- `SearchChannelType.java` - 检索通道类型枚举
- `SearchContext.java` - 检索上下文
- `SearchChannelResult.java` - 检索通道结果

#### 检索通道实现
- `VectorGlobalSearchChannel.java` - 向量全局检索通道
- `IntentDirectedSearchChannel.java` - 意图定向检索通道

#### 后置处理器
- `SearchResultPostProcessor.java` - 后置处理器接口
- `DeduplicationPostProcessor.java` - 去重处理器
- `RerankPostProcessor.java` - Rerank 处理器

#### 核心引擎
- `MultiChannelRetrievalEngine.java` - 多通道检索引擎

#### 配置和文档
- `application-search.yml` - 检索配置文件
- `multi-channel-retrieval.md` - 架构说明文档

### 2. 修改文件

- `RetrievalEngine.java` - 集成多通道检索引擎

## 架构设计

### 核心思想

采用**责任链 + 策略模式**的组合：
- **策略模式**：不同的检索通道实现不同的检索策略
- **责任链模式**：后置处理器形成处理链，依次处理检索结果

### 工作流程

```
用户问题
    ↓
【多通道并行检索】
    ├─→ VectorGlobalSearchChannel（条件触发）
    └─→ IntentDirectedSearchChannel（始终执行）
    ↓
【后置处理器链】
    ├─→ DeduplicationPostProcessor（去重）
    └─→ RerankPostProcessor（重排序）
    ↓
【返回最终结果】
```

### 关键特性

1. **条件触发的双路召回**
   - 意图识别成功：只执行意图定向检索
   - 意图识别失败或置信度低：同时执行全局检索和意图定向检索

2. **并行执行**
   - 所有启用的检索通道并行执行，提升性能

3. **统一后处理**
   - 去重：合并多个通道的结果，保留高优先级通道的结果
   - Rerank：对合并后的结果进行重排序

4. **易于扩展**
   - 新增检索通道：实现 `SearchChannel` 接口
   - 新增后置处理器：实现 `SearchResultPostProcessor` 接口
   - 无需修改核心代码

## 解决方案对比

| 方案 | 覆盖率 | 准确率 | 性能 | 扩展性 |
|------|--------|--------|------|--------|
| **原方案**（仅意图识别） | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **新方案**（多通道检索） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 新方案优势

1. **覆盖率提升**：全局检索兜底，即使意图识别失败也能检索到相关文档
2. **准确率保持**：意图定向检索优先，保证精确性
3. **性能可控**：条件触发，只在必要时启用全局检索
4. **扩展性强**：新增通道或处理器无需修改核心代码

## 使用示例

### 1. 基本使用

```java
@Service
public class RAGService {
    @Autowired
    private MultiChannelRetrievalEngine retrievalEngine;

    public void search(String question) {
        List<SubQuestionIntent> intents = ...;
        List<RetrievedChunk> chunks = retrievalEngine.retrieveKB(intents, 5);
        // 使用检索结果
    }
}
```

### 2. 新增检索通道

```java
@Component
public class KeywordESSearchChannel implements SearchChannel {
    @Override
    public String getName() {
        return "KeywordESSearch";
    }

    @Override
    public boolean isEnabled(SearchContext context) {
        // 判断是否启用
        return containsKeywords(context.getMainQuestion());
    }

    @Override
    public SearchChannelResult search(SearchContext context) {
        // 实现 ES 检索逻辑
        // ...
    }
}
```

### 3. 新增后置处理器

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
    public List<RetrievedChunk> process(...) {
        // 实现版本过滤逻辑
        // ...
    }
}
```

## 配置说明

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

## 未来扩展

1. **ES 关键词检索通道**：基于 Elasticsearch 的全文检索
2. **版本过滤处理器**：只保留最新版本的文档
3. **分数归一化处理器**：统一不同通道的分数尺度
4. **缓存机制**：对检索结果进行缓存
5. **监控和统计**：记录各通道的命中率、耗时等指标

## 测试建议

1. **单元测试**
   - 测试各检索通道的独立功能
   - 测试各后置处理器的处理逻辑

2. **集成测试**
   - 测试多通道并行执行
   - 测试后置处理器链的执行顺序

3. **性能测试**
   - 对比单通道和多通道的性能差异
   - 测试不同配置下的性能表现

4. **覆盖率测试**
   - 对比原方案和新方案的检索覆盖率
   - 测试意图识别失败时的兜底效果

## 注意事项

1. **通道优先级**：数字越小优先级越高，影响去重时的结果保留策略
2. **处理器顺序**：`order` 决定执行顺序，去重应该最先执行，Rerank 应该最后执行
3. **性能考虑**：启用过多通道会增加延迟，建议根据实际需求选择性启用
4. **配置调优**：`confidence-threshold`、`top-k-multiplier` 等参数需要根据实际效果调整

## 总结

本次重构实现了一个**可扩展的多通道检索架构**，解决了意图识别覆盖率不足的问题，同时保持了高准确率和良好的扩展性。通过条件触发的双路召回策略，在覆盖率和性能之间取得了良好的平衡。

新架构的核心优势：
- ✅ **高覆盖率**：全局检索兜底
- ✅ **高准确率**：意图定向检索优先
- ✅ **易扩展**：新增通道或处理器无需修改核心代码
- ✅ **灵活配置**：通过配置文件控制行为
- ✅ **性能可控**：条件触发，按需启用
