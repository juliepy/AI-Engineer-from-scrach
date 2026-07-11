# 02-RAG_basic：RAG 核心知识点代码示例

> 每个文件对应一个知识点，可独立运行，无需 API Key。

## 目录

| 文件 | 主题 |
|------|------|
| `01-wash_Data.py` | 数据清洗：去噪、去重、标准化 |
| `02-pdf-load.py` | 文档解析：PDF / Word / HTML / MD |
| `03-chunking_ps.py` | 分块策略：固定窗口、句子、语义分块对比 |
| `04-langchain_text_splitter.py` | LangChain 文本分块器用法 |
| `05-sentence_transformer.py` | SentenceTransformer 编码与向量归一化 |
| `06-vector_database.py` | FAISS 向量数据库：构建索引 + Top-K 检索 |
| `07-vector_search.py` | 向量检索（语义相似度） |
| `08-bm25_search.py` | 关键词检索（BM25） |
| `09-hybrid_search.py` | 混合检索：向量 + BM25 线性加权融合 |
| `10-rrf_search.py` | RRF 多路排名融合 |
| `11-reranking.py` | Step-back 检索 & Cross-Encoder 重排序 |
| `12-mmr_crossencoder.py` | MMR 去冗余选择 & Cross-Encoder 精排 |

## 安装依赖

```bash
pip install -r requirements.txt
```

## 模型说明

| 用途 | 模型 | 运行方式 |
|------|------|----------|
| Embedding | `BAAI/bge-small-zh-v1.5` | 本地（首次自动下载） |
| 向量索引 | FAISS `IndexFlatIP` | 本地 |
| 关键词检索 | BM25 + jieba 分词 | 本地 |
