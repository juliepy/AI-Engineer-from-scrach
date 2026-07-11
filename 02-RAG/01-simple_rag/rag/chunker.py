"""
离线流水线 Step 2：结构化分块（Chunking）
策略：固定窗口 + 重叠（overlap），保留来源元数据
"""
from dataclasses import dataclass, field
from typing import List
from .document_parser import Document


@dataclass
class Chunk:
    """文本块，携带溯源信息"""
    text: str
    source: str
    chunk_id: str
    metadata: dict = field(default_factory=dict)


class TextChunker:
    """
    滑动窗口分块器
    chunk_size : 每块目标字符数
    overlap    : 相邻块重叠字符数（保留上下文连贯性）
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, doc: Document) -> List[Chunk]:
        text = doc.content
        chunks: List[Chunk] = []
        start = 0
        idx = 0

        while start < len(text):
            end = start + self.chunk_size

            # 尽量在句子/段落边界截断，避免截断句子中间
            if end < len(text):
                end = self._find_boundary(text, end)

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    source=doc.source,
                    chunk_id=f"{doc.source}#{idx}",
                    metadata={**doc.metadata, "chunk_index": idx},
                ))
                idx += 1

            # 下一块起点往回退 overlap 个字符
            start = end - self.overlap if end - self.overlap > start else end

        return chunks

    def _find_boundary(self, text: str, pos: int) -> int:
        """从 pos 往前找最近的句子/段落边界"""
        for sep in ('\n\n', '\n', '。', '！', '？', '.', '!', '?', ' '):
            idx = text.rfind(sep, pos - 100, pos)
            if idx != -1:
                return idx + len(sep)
        return pos
