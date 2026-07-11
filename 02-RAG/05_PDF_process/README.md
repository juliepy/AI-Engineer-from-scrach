# Lesson 2 — PDF Parsing 101

**完整讲义已迁入 Jupyter Notebook**（原 `slides.md` 已删除），按顺序学习：

| 顺序 | Notebook | 主题 |
|------|----------|------|
| 0 | [06-demo.ipynb](06-demo.ipynb) | 课程总览 + 全流程 Demo |
| 1 | [01_detect_pdf_type.ipynb](01_detect_pdf_type.ipynb) | 类型识别 + 工具选型 |
| 2 | [02_extract_text.ipynb](02_extract_text.ipynb) | 文本提取 + 多栏 |
| 3 | [03_extract_tables.ipynb](03_extract_tables.ipynb) | 表格抽取 |
| 4 | [04_ocr_scanned.ipynb](04_ocr_scanned.ipynb) | 扫描件 OCR |
| — | [04_llm_ocr_demo.ipynb](04_llm_ocr_demo.ipynb) | LLM 后处理（选修） |
| 5 | [05_full_pipeline.ipynb](05_full_pipeline.ipynb) | **索引** → 05a / 05b / 05c |
| 5a | [05a_part1_pipeline.ipynb](05a_part1_pipeline.ipynb) | 工程化解析 → JSONL chunk（必选） |
| 5b | [05b_part2_advanced_parsing.ipynb](05b_part2_advanced_parsing.ipynb) | Marker / LlamaParse（选修） |
| 5c | [05c_part3_rag_compare.ipynb](05c_part3_rag_compare.ipynb) | FAISS → RAG 多路径对比（选型） |
| 5d | [05d_production_rag_pipeline.ipynb](05d_production_rag_pipeline.ipynb) | **生产流水线**：统一索引 + Rerank + 一次回答（必选） |

## 教学目标

从复杂 PDF（数字版 / 扫描版 / 多栏 / 含表格 / 含图）中**可靠地**提取结构化内容，
为 RAG 检索准备**干净、可追溯**的 chunk。

---

从复杂 PDF（数字版 / 扫描版 / 多栏 / 含表格 / 含图）中**可靠地**提取结构化内容，
为 RAG 检索准备**干净、可追溯**的 chunk。

---

## 1. PDF 三种类型

| 类型 | 特征 | 文本能直接复制？ | 处理工具 |
|------|------|------------------|----------|
| **数字 PDF** | 由 Word / LaTeX 导出 | ✅ 能 | pdfplumber / PyMuPDF |
| **扫描 PDF** | 整页是图片（拍照、扫描） | ❌ 不能 | pdf2image + Tesseract OCR |
| **混合 PDF** | 大部分数字，少量页扫描 | 部分能 | 按页判断 + 两种策略组合 |

**判断方法**：用 PyMuPDF 提文本，如果 `len(text) < 阈值` 但 `page.get_images()` 有图 → 大概率是扫描页。

---

## 2. 工具选型对比

| 工具 | 强项 | 弱项 | 推荐场景 |
|------|------|------|----------|
| **PyPDF2** | 纯 Python、零依赖 | 文本提取质量差、不支持表格 | 只做文本拼接，要求最低依赖 |
| **pdfplumber** | 版面感知、内置表格提取 | 速度慢 | **正文 + 表格**的首选 |
| **PyMuPDF (fitz)** | 速度极快、API 强大、能提图 | 安装包大 | 大批量、需要图片/坐标 |
| **camelot** | 表格抽取质量最好 | 仅 lattice/stream，复杂表格仍会错 | 关键报表 / 财务数据 |
| **pdf2image + Tesseract** | 唯一能处理扫描件 | 慢、对中文需要训练数据 | 扫描件 OCR |
| **Unstructured** | 统一接口处理 PDF/Word/HTML | 是个大库、依赖多 | 多格式统一入口 |

**经验组合**：`PyMuPDF`（速度）+ `pdfplumber`（表格）+ `Tesseract`（OCR 兜底）

---

## 3. 完整解析流水线

```
PDF 文件
  ├── 1. 按页打开（流式，避免大文件 OOM）
  ├── 2. 判断该页类型（数字 / 扫描）
  ├── 3. 数字页：
  │      ├── 检测多栏布局（按 bbox.x0 聚类）
  │      ├── 按阅读顺序抽取文本块
  │      └── 用 pdfplumber 抽取表格
  ├── 4. 扫描页：
  │      ├── pdf2image 渲染为图片
  │      └── Tesseract OCR
  ├── 5. 文本清洗：
  │      ├── 去除页眉页脚（前后页相同的行）
  │      ├── 合并跨行单词（行尾连字符）
  │      └── 标准化空白
  ├── 6. Chunk 切分：
  │      ├── 按 token 数（不是字符数！）
  │      ├── 保留 overlap（通常 10-15%）
  │      └── 元数据：file # page # chunk_id
  └── 7. 向量化 + 入库
```
