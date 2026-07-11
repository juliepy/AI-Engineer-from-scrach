# GraphRAG + 混合检索

纯向量检索有硬伤——用 Vector + BM25 + Graph 三路并行 + RRF 融合，搭出工业级 RAG。

---

## 整体架构

```
文档
 │
 ├─► ChromaDB ──► 向量检索 ─────────────┐
 │                                      │
 ├─► BM25 索引 ──► 关键词检索 ──────────┤──► RRF 融合 ──► 最终答案
 │                                      │
 └─► Neo4j 图 ──► 图检索（多跳）────────┘
      │
      LangChain GraphCypherQAChain
```

---

## 文件结构

```
04-graph_rag进阶/
├── README.md                          # 本文件
├── requirements.txt                   # Python 依赖清单
├── SLIDES.md                          # Marp 课程幻灯片
├── .env.example                       # 环境变量模板
├── 01_vector_limitations.ipynb        # Notebook：向量检索局限演示（含 BM25 对比）
├── 02_knowledge_graph_builder.ipynb   # Notebook：Neo4j 知识图谱构建（单跳/双跳/三跳查询）
├── 03_hybrid_retrieval_rrf.ipynb      # Notebook：三路检索 + RRF 融合
└── 04_graphrag_pipeline.ipynb         # Notebook：LangChain 端到端 GraphRAG Pipeline
```

---

## 快速开始

### 环境准备

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（Notebook 4 需要）
cp .env.example .env
# 编辑 .env，填入：
#   OPENAI_API_KEY=sk-...   （DeepSeek 或 OpenAI Key）
#   NEO4J_PASSWORD=password

# 3. 启动 Neo4j（Notebook 2、4 需要；Notebook 4 还需 APOC 插件）
docker run -d --name neo4j-apoc \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_dbms_security_procedures_unrestricted=apoc.* \
  -e NEO4J_dbms_security_procedures_allowlist=apoc.* \
  neo4j:latest
# 浏览器访问：http://localhost:7474
# 验证 APOC：RETURN apoc.version()
```

### 运行顺序

| Notebook | 依赖 | 说明 |
|----------|------|------|
| `01_vector_limitations.ipynb` | 无需 Neo4j | 向量 vs BM25 对比，三个失败场景演示 |
| `02_knowledge_graph_builder.ipynb` | 需要 Neo4j | 构建知识图谱，演示多跳 Cypher 查询 |
| `03_hybrid_retrieval_rrf.ipynb` | 无需 Neo4j | 三路检索 + RRF 融合排序 |
| `04_graphrag_pipeline.ipynb` | 需要 Neo4j + LLM Key | LangChain 端到端 GraphRAG Pipeline |

---

## 三个经典失败场景

| 场景 | 查询示例 | 向量检索 | BM25 | 图检索 |
|------|---------|---------|------|--------|
| 精确关键词 | `索尼降噪耳机推荐` | ✅ 语义匹配 | ❌ 词元不精确 | — |
| 精确型号 | `WH-1000XM5` | ⚠️ 依赖子词分词 | ✅ 精确匹配 | — |
| 多跳推理 | `苹果CEO在哪城市读大学？` | ❌ 只能第一跳 | ❌ 只能第一跳 | ✅ 图遍历 |
| 数值/日期 | `1975年4月4日` | ❌ 数字语义相近混淆 | ✅ 精确词元 | — |

---

## 知识点清单

- [x] 纯向量检索三大局限：精确关键词、多跳推理、数值精度
- [x] jieba 中文分词 + BM25 精确关键词检索
- [x] Knowledge Graph：Node、Relationship、Property 三要素
- [x] Neo4j + Cypher 查询（单跳、双跳、三跳）
- [x] RRF 公式：`score(d) = Σ 1/(k + rank_i(d))`，三路检索融合
- [x] LangChain `LLMGraphTransformer` 实体抽取
- [x] `Neo4jGraph` + `GraphCypherQAChain` 端到端 Pipeline

---

