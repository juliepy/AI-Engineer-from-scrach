# =============================================================================
#  LangChain Text Splitter 四种分块方式对比
# =============================================================================
#
#  ┌──────────────────────────────────────────────────────────────────────────┐
#  │                         原始文本 / Markdown                               │
#  └──────┬──────────────────┬──────────────────┬──────────────────┬──────────┘
#         │                  │                  │                  │
#         ▼                  ▼                  ▼                  ▼
#  CharacterText    RecursiveCharacter   MarkdownHeader      SemanticChunker
#  Splitter         TextSplitter         TextSplitter        (Embedding相似度)
#  固定分隔符一刀切   递归多级分隔(首选)    按标题层级分块       语义自动切分
#         │                  │                  │                  │
#         ▼                  ▼                  ▼                  ▼
#       chunks             chunks          docs+metadata       semantic chunks
#                                                                  │
#                                                              Embeddings
#
# =============================================================================

import sys
import os
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)

text = (
    "第一段：公司成立于2010年，专注于人工智能领域的研发与应用。\n\n"
    "第二段：标准工作时间为周一至周五，每天9:00-18:00，午休12:00-13:00。"
    "公司每月15日发放工资，提供五险一金、带薪年假、节日福利及年终奖金。\n\n"
    "第三段：员工应遵守职业道德，保护公司机密，禁止从事与公司利益相冲突的行为。"
)

# ── 1. 固定字符分块 ───────────────────────────────────────────────────────────
print("=" * 60)
print("【1】CharacterTextSplitter（固定分隔符）")
fixed = CharacterTextSplitter(separator="\n\n", chunk_size=60, chunk_overlap=5)
for i, chunk in enumerate(fixed.split_text(text)):
    print(f"  chunk-{i}: {chunk}")

# ── 2. 递归字符分割（RAG 首选）────────────────────────────────────────────────
print("=" * 60)
print("【2】RecursiveCharacterTextSplitter（递归多级，RAG首选）")
recursive = RecursiveCharacterTextSplitter(
    chunk_size=40,
    chunk_overlap=5,
    separators=["\n\n", "\n", "。", "，", ""],
)
for i, chunk in enumerate(recursive.split_text(text)):
    print(f"  chunk-{i}: {chunk}")

# ── 3. Markdown 按标题层级分块 ────────────────────────────────────────────────
print("=" * 60)
print("【3】MarkdownHeaderTextSplitter（携带标题元数据）")
md = (
    "# 员工手册\n公司简介内容。\n\n"
    "## 工作时间\n每天9:00-18:00。\n\n"
    "## 薪酬福利\n每月15日发薪。\n"
)
headers = [("#", "章"), ("##", "节")]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
for doc in md_splitter.split_text(md):
    print(f"  metadata={doc.metadata}  内容: {doc.page_content}")

# ── 4. 语义分块：使用 DeepSeek Embeddings ────────────────────────────────────
print("=" * 60)
print("【4】SemanticChunker（DeepSeek Embeddings 语义切分）")
try:
    from langchain_experimental.text_splitter import SemanticChunker
    from langchain_huggingface import HuggingFaceEmbeddings

    # 本地免费模型，首次运行自动下载（~90MB）
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    semantic_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
    )
    semantic_chunks = semantic_splitter.create_documents([text])
    for i, doc in enumerate(semantic_chunks):
        print(f"  semantic-chunk-{i}: {doc.page_content}")
except ImportError as e:
    print(f"  缺少依赖：{e}")
    print("  安装：pip install langchain-experimental langchain-huggingface sentence-transformers")
except Exception as e:
    print(f"  语义分块失败：{e}")
