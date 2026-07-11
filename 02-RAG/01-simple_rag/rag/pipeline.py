"""
RAG Pipeline 总装：离线流水线 + 在线问答的完整闭环
"""
from pathlib import Path
from typing import List

from .document_parser import DocumentParser
from .chunker import TextChunker
from .embedder import Embedder
from .vector_store import VectorStore
from .retriever import Retriever
from .generator import Generator


class RAGPipeline:
    """
    最小 RAG 闭环
    ┌─────────────────────────────────────────┐
    │  离线流水线                               │
    │  文件 → 解析 → 分块 → Embed → VectorStore │
    ├─────────────────────────────────────────┤
    │  在线问答                                 │
    │  Query → Embed → 检索 → Prompt → LLM     │
    └─────────────────────────────────────────┘
    """

    def __init__(
        self,
        api_key: str | None = None,
        index_path: str = "./index",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        top_k: int = 5,
        use_mmr: bool = False,
        stream: bool = False,
    ):
        self.stream = stream
        self.parser  = DocumentParser()
        self.chunker  = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap)
        self.embedder = Embedder(api_key=api_key)
        self.store    = VectorStore(index_path=index_path)
        self.retriever = Retriever(
            embedder=self.embedder,
            vector_store=self.store,
            top_k=top_k,
            use_mmr=use_mmr,
        )
        self.generator = Generator(api_key=api_key)

    # ──────────────────────── 离线：构建索引 ────────────────────────

    def build_index(self, doc_dir: str, force_rebuild: bool = False) -> None:
        """
        扫描 doc_dir 下所有支持格式的文件，解析→分块→嵌入→写入索引
        force_rebuild=False 时若已存在索引则跳过
        """
        if not force_rebuild and self.store.load():
            print(f"[Pipeline] 已加载现有索引（{self.store.total} 个块），跳过重建。")
            return

        supported = {".pdf", ".docx", ".doc", ".html", ".htm", ".md", ".txt"}
        files = [
            p for p in Path(doc_dir).rglob("*")
            if p.suffix.lower() in supported
        ]

        if not files:
            raise FileNotFoundError(f"在 {doc_dir} 下未找到支持的文档文件。")

        print(f"[Pipeline] 发现 {len(files)} 个文件，开始构建索引...")

        all_chunks = []
        for file in files:
            print(f"  解析: {file.name}")
            doc = self.parser.parse(str(file))
            chunks = self.chunker.split(doc)
            all_chunks.extend(chunks)

        print(f"[Pipeline] 共生成 {len(all_chunks)} 个文本块，开始嵌入...")
        texts = [c.text for c in all_chunks]
        embeddings = self.embedder.embed(texts)

        self.store.add(all_chunks, embeddings)
        self.store.save()
        print("[Pipeline] 索引构建完成！")

    # ──────────────────────── 在线：问答 ────────────────────────

    def ask(self, question: str) -> str:
        """
        完整在线问答流程：
        Query → Embed → 向量检索 → 拼装 Prompt → DeepSeek 生成
        """
        print(f"\n[Pipeline] 问题：{question}")

        # 1. 检索
        retrieved = self.retriever.retrieve(question)
        print(f"[Pipeline] 检索到 {len(retrieved)} 个相关块：")
        for score, chunk in retrieved:
            preview = chunk.text[:80].replace('\n', ' ')
            print(f"  score={score:.3f} | {preview}...")

        # 2. 生成
        if self.stream:
            answer_parts = []
            print("\n[DeepSeek 回答]\n")
            for token in self.generator.generate_stream(question, retrieved):
                print(token, end="", flush=True)
                answer_parts.append(token)
            print()
            return "".join(answer_parts)
        else:
            answer = self.generator.generate(question, retrieved)
            return answer
