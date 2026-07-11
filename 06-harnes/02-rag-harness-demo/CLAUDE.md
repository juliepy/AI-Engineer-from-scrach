# RAG Harness Demo — AI Layer

这是一个用于教学的 RAG（检索增强生成）全栈项目。
Stack：**FastAPI**（后端）+ **静态 HTML/JS**（前端）+ **TF-IDF 检索**（索引）。

---

## RAG 管道（五个阶段）

| 阶段 | 文件 | 核心函数/类 |
|------|------|------------|
| **ingest** | `app/rag.py` | `RAGPipeline.ingest_text / ingest_directory` |
| **chunk** | `app/chunker.py` | `chunk_text(doc_id, text, chunk_size, overlap)` |
| **index** | `app/indexer.py` | `TfidfIndex.add_chunks / search` |
| **retrieve** | `app/retriever.py` | `retrieve(index, query, top_k)` |
| **generate** | `app/generator.py` | `generate_answer(query, hits)` |

每个阶段独立成文件，便于讲解和替换。

---

## 命名规范

| 层级 | 规范 | 示例 |
|------|------|------|
| Python 文件 | `snake_case` | `chunker.py`, `indexer.py` |
| Python 类 | `PascalCase` | `TfidfIndex`, `RAGPipeline`, `Chunk` |
| Python 函数/变量 | `snake_case` | `chunk_text`, `top_k`, `doc_id` |
| 测试文件 | `test_<module>.py` | `test_chunker.py`, `test_rag.py` |
| API 路由 | `/api/<resource>` | `/api/query`, `/api/ingest` |
| 知识库文档 | `<topic>.txt` | `rag_basics.txt`, `chunking.txt` |

---

## 代码模式

**Chunk 数据类**（`app/chunker.py`）：`@dataclass(frozen=True)`，字段为 `doc_id / text / index`。

**TfidfIndex**（`app/indexer.py`）：`add_chunks()` 触发重新 fit，`search()` 返回 `list[IndexedChunk]`，score 为 cosine 相似度。

**RAGPipeline**（`app/rag.py`）：组合上面所有阶段，`query()` 返回 `QueryResult(query, answer, hits)`。

**FastAPI**（`api/server.py`）：路由只做请求解包和响应组装，不含业务逻辑；业务逻辑全在 `app/`。

**测试 mock**：任何调用外部 LLM 的代码，测试中必须 mock client，不依赖真实 API Key。

---

## 构建与验证命令

| 步骤 | 命令 | 说明 |
|------|------|------|
| 全量测试 | `python scripts/validate.py` | 唯一质量门，Harness 用这个 |
| 单模块测试 | `python -m unittest tests/test_chunker.py -v` | 局部调试 |
| 启动服务 | `uvicorn api.server:app --reload --port 8000` | 本地演示 |
| 代码检查 | `ruff check app` | 每次编辑后自动触发（PostToolUse hook） |

---

## 硬性规则

- 不允许读写真实 `.env` 文件；不允许递归删除目录。
- 不允许跳过任务验证直接标记为完成——每个 Task 的 `Validate:` 命令必须先通过。
- 每个 RAG 阶段保持独立文件，不要把多个阶段合并进同一个文件。
- 改动 `app/` 下任何文件后，**相应测试必须仍然通过**。
- 测试中调用 LLM 相关代码时，必须 mock，不调用真实 API。

---

## 工作流规则

- 编写代码前先 `/plan`，有 plan 文件才能 `/implement`。
- `/implement` 执行每个 Task 后立刻跑 Task 的 `Validate:` 命令；不通过不进入下一 Task。
- 全部 Task 完成后跑 `python scripts/validate.py`；通过才算 Done。
- Stop hook 会在 Agent 结束前自动运行验证门；未通过时会阻止结束。
