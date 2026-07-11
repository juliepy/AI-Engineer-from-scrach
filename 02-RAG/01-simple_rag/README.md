# 01-simple_rag：最小 RAG 闭环实现

> 模型：DeepSeek | 向量库：FAISS | 框架：纯 Python（无 LangChain）

## 架构图

```
【离线流水线】
文档文件 (PDF/Word/HTML/MD/TXT)
  └─ DocumentParser   解析 + 清洗
  └─ TextChunker      滑动窗口分块（含重叠）
  └─ Embedder         批量调用 Embedding API
  └─ VectorStore      写入 FAISS 索引并持久化

【在线问答】
用户 Query
  └─ Embedder         Query 向量化
  └─ VectorStore      FAISS Top-K 检索
  └─ Retriever        (可选) MMR 去冗余
  └─ Generator        拼装 Prompt → DeepSeek 生成答案
```

## 代码设计流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        【离线索引阶段】                               │
│                                                                     │
│  PDF / Word / HTML / MD / TXT                                       │
│            │                                                        │
│            ▼  document_parser.py                                    │
│  ┌─────────────────────┐                                            │
│  │   DocumentParser    │  多格式解析 + 清洗噪声字符                   │
│  └──────────┬──────────┘                                            │
│             │  纯文本列表                                            │
│             ▼  chunker.py                                           │
│  ┌─────────────────────┐                                            │
│  │    TextChunker      │  固定窗口分块（size=500, overlap=50）        │
│  └──────────┬──────────┘                                            │
│             │  chunks[]                                             │
│             ▼  embedder.py                                          │
│  ┌─────────────────────┐                                            │
│  │      Embedder       │  SentenceTransformer 本地推理               │
│  │                     │  模型：BAAI/bge-small-zh-v1.5              │
│  │                     │  normalize_embeddings=True（L2 归一化）     │
│  └──────────┬──────────┘                                            │
│             │  float32 向量矩阵（dim=512）                           │
│             ▼  vector_store.py                                      │
│  ┌─────────────────────┐                                            │
│  │    VectorStore      │  faiss.IndexFlatIP 写入 + 持久化到磁盘      │
│  └─────────────────────┘                                            │
│                  faiss.index / chunks.pkl / meta.json               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        【在线问答阶段】                               │
│                                                                     │
│  用户 Query                                                         │
│       │                                                             │
│       ▼  embedder.py                                                │
│  ┌─────────────────────┐                                            │
│  │      Embedder       │  同离线同模型：bge-small-zh-v1.5            │
│  └──────────┬──────────┘                                            │
│             │  query_vec（dim=512，已归一化）                        │
│             ▼  vector_store.py                                      │
│  ┌─────────────────────┐                                            │
│  │    VectorStore      │  IndexFlatIP.search() → Top-K 候选         │
│  │                     │  内积 = 余弦相似度（归一化后等价）           │
│  └──────────┬──────────┘                                            │
│             │  (score, chunk)[]                                     │
│             ▼  retriever.py                                         │
│  ┌─────────────────────┐                                            │
│  │      Retriever      │  MMR 去冗余 → 最终上下文 chunks             │
│  └──────────┬──────────┘                                            │
│             │  context_str                                          │
│             ▼  generator.py                                         │
│  ┌─────────────────────┐                                            │
│  │      Generator      │  拼装 Prompt → DeepSeek Chat API           │
│  │                     │  模型：deepseek-chat                       │
│  │                     │  base_url：api.deepseek.com                │
│  └──────────┬──────────┘                                            │
│             │                                                       │
│             ▼                                                       │
│         最终答案（流式 / 非流式）                                     │
└─────────────────────────────────────────────────────────────────────┘

                     ┌─────────────────────┐
                     │    pipeline.py      │
                     │    RAGPipeline      │  统一编排以上所有步骤
                     │    .build_index()   │  → 离线阶段入口
                     │    .ask()           │  → 在线阶段入口
                     └─────────────────────┘

  模型总览
  ┌─────────────────┬───────────────────────────┬────────────────┐
  │ 阶段            │ 模型                       │ 运行方式       │
  ├─────────────────┼───────────────────────────┼────────────────┤
  │ Embedding       │ BAAI/bge-small-zh-v1.5    │ 本地（无需Key）│
  │ 向量索引        │ FAISS IndexFlatIP          │ 本地           │
  │ 生成（LLM）     │ deepseek-chat              │ API（需Key）   │
  └─────────────────┴───────────────────────────┴────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录 `.env` 中填写：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
```

### 3. 运行演示

```bash
# 运行预设4个演示问题
python main.py --demo

# 交互式问答
python main.py

# 流式输出 + 强制重建索引
python main.py --stream --rebuild

# 自定义文档目录
python main.py --doc-dir ./my_docs --top-k 5
```

## 文件结构

```
01-simple_rag/
├── main.py                 # 入口脚本
├── requirements.txt        # 依赖
├── docs/                   # 示例知识库文档
│   ├── company_hr_policy.md
│   └── product_manual.md
├── index/                  # 自动生成：FAISS 索引文件
│   ├── faiss.index
│   ├── chunks.pkl
│   └── meta.json
└── rag/
    ├── __init__.py
    ├── pipeline.py         # 总装：RAGPipeline
    ├── document_parser.py  # Step1: 多格式文档解析
    ├── chunker.py          # Step2: 滑动窗口分块
    ├── embedder.py         # Step3: 批量 Embedding
    ├── vector_store.py     # Step4: FAISS 向量存储
    ├── retriever.py        # Online: Top-K + MMR 检索
    └── generator.py        # Online: DeepSeek 生成
```

## 核心设计决策

| 问题 | 选择 | 原因 |
|------|------|------|
| 向量索引 | FAISS IndexFlatIP | 小规模精确检索，无需调参 |
| 相似度 | 余弦相似度 | L2 归一化后内积 = 余弦，FAISS 原生支持 |
| 去冗余 | MMR | 平衡相关性与多样性，避免重复上下文 |
| Embedding | BAAI/bge-small-zh-v1.5 | 本地 SentenceTransformer，无需 API Key |
| 分块策略 | 固定窗口 + 重叠 | 简单可靠，overlap 保留块间上下文 |

## 生产建议

- **嵌入缓存**：对已处理文件用哈希跳过，避免重复调用 API
- **增量更新**：文件变更时只重建变更块的向量
- **ANN 升级**：文档 > 10万块时换用 `IndexIVFFlat` 或 `HNSW`
- **混合检索**：加入 BM25 做关键字检索，两路结果 RRF 融合
- **重排序**：加 Cross-Encoder（如 `bge-reranker`）精排 Top-K 结果
