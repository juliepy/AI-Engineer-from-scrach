# 03-high_level_RAG：高级 RAG 架构示例

> 每个文件对应一种高级 RAG 范式，可独立运行。  
> 语料为内置公司员工手册片段，检索使用 FAISS + SentenceTransformer，LLM 调用 DeepSeek。

## 目录

| 序号 | 文件 | 主题 | 一句话 |
|------|------|------|--------|
| 8.1 | `01-graph_rag.py` | **GraphRAG** | 建知识图谱，沿子图检索，适合多跳推理 |
| 8.2 | `02-agentic_rag.py` | **Agentic RAG** | Agent 自主决定何时检索、检索几次 |
| 8.3 | `03-self_rag.py` | **Self-RAG** | 生成前后四步自省：要不要检索、文档是否相关、是否有依据 |
| 8.4 | `04-corrective_rag.py` | **Corrective RAG** | 评估检索质量，不达标则改写查询并补充检索 |
| 8.5 | `05-adaptive_rag.py` | **Adaptive RAG** | 路由分类：直接回答 / 单跳检索 / 多跳检索 |

## 五种范式对比（讲课用）

| 范式 | 核心思路 | 与普通 RAG 的区别 |
|------|----------|-------------------|
| GraphRAG | 实体-关系图 + 子图检索 | 能做多跳关系推理，不只靠向量相似度 |
| Agentic RAG | LLM + Tool 多步决策 | 检索次数和关键词由 Agent 决定，非固定一次 |
| Self-RAG | Retrieve? → IsRel? → IsSup? → IsUse? | 强调检索与答案质量的自我反思 |
| Corrective RAG | 检索评估 → 纠正 → 精炼 → 生成 | 检索不好时会主动改写并补充证据 |
| Adaptive RAG | 问题分类 → 路由到不同管道 | 简单问题不检索，复杂问题多步检索 |

## 安装与运行

```bash
pip install -r requirements.txt
```

配置 API Key（二选一）：

```bash
# 在本目录 .env 中
DEEPSEEK_API_KEY=your_key_here
```

运行示例：

```bash
python 01-graph_rag.py
python 02-agentic_rag.py
python 03-self_rag.py
python 04-corrective_rag.py
python 05-adaptive_rag.py
```

## 建议讲课顺序

1. **GraphRAG** — 引入「结构化知识」视角（离线建图 + 在线子图检索）
2. **Agentic RAG** — 从固定流水线到 Agent 决策循环
3. **Self-RAG** — 在 Agent 思路上聚焦「质量自省」
4. **Corrective RAG** — 解决「检索错了怎么办」
5. **Adaptive RAG** — 用路由控制成本，与 Agentic 对比收尾

## 依赖说明

| 组件 | 用途 |
|------|------|
| `sentence-transformers` | 本地 Embedding |
| `faiss-cpu` | 向量检索 |
| `langchain-deepseek` | LLM 调用 |
| `langchain-experimental` | GraphRAG 图抽取（`LLMGraphTransformer`） |
