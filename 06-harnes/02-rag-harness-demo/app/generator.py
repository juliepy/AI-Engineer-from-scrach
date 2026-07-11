from __future__ import annotations

from app.indexer import IndexedChunk


def generate_answer(query: str, hits: list[IndexedChunk]) -> str:
    """Template-based answer for teaching (no external LLM required)."""
    if not hits:
        return "未在知识库中找到相关内容，请尝试换个问法或先导入文档。"

    lines = [f"关于「{query}」，知识库中的相关片段如下：", ""]
    for rank, hit in enumerate(hits, start=1):
        lines.append(f"{rank}. [{hit.chunk.doc_id}] {hit.chunk.text}")
    lines.append("")
    lines.append("（教学演示：此处由检索结果直接拼接，生产环境可替换为 LLM 生成。）")
    return "\n".join(lines)
