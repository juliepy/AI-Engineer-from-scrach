# =============================================================================
#  Parent-Child Chunking  逻辑图
# =============================================================================
#
#  ┌─────────────────────────────────────────────────────────────────────────┐
#  │                         原始长文档 (full_text)                           │
#  └───────────────────────────────┬─────────────────────────────────────────┘
#                                  │  build_parent_child_chunks()
#                                  │  按 child_size 字符切分
#                                  ▼
#  ┌─────────────────────────────────────────────────────────────────────────┐
#  │  ParentChunk  (parent_id="doc-001",  text=完整原文)                      │
#  │                                                                         │
#  │   children ──►  ChildChunk-0  │  ChildChunk-1  │ … │  ChildChunk-N     │
#  │                 (child_id,        (child_id,                            │
#  │                  parent_id,        parent_id,                           │
#  │                  text=小块文本)     text=小块文本)                        │
#  └─────────────────────────────────────────────────────────────────────────┘
#
#  ── 索引阶段 ──────────────────────────────────────────────────────────────
#
#   ChildChunk.text  ──► Embedding 模型 ──► 向量数据库
#                         (仅对小块做 embed，payload 存 parent_id)
#
#  ── 检索阶段 ──────────────────────────────────────────────────────────────
#
#   用户 Query
#      │
#      ▼
#   Embedding 模型
#      │  向量相似度检索
#      ▼
#   命中 ChildChunk  (child_id="doc-001-child-3")
#      │  child_to_parent[child_id]  →  parent_id
#      ▼
#   parent_store[parent_id]  →  ParentChunk.text (完整原文)
#      │
#      ▼
#   送给 LLM 生成最终答案
#
# =============================================================================

import sys
from dataclasses import dataclass
from typing import List

sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class ParentChunk:
    parent_id: str
    text: str
    children: List["ChildChunk"]


@dataclass
class ChildChunk:
    child_id: str
    parent_id: str
    text: str  # 小块，用于 embedding

# 索引阶段：只对 ChildChunk.text 做 embed，payload 带 parent_id
# 检索阶段：命中 child_id -> 查 ParentChunk.text 作为生成上下文


def build_parent_child_chunks(
    doc_id: str,
    full_text: str,
    child_size: int = 50,
) -> ParentChunk:
    """将一段长文本切成若干小块，构建 Parent-Child 结构（按字符数切分，适合中文）。"""
    child_texts = [
        full_text[i : i + child_size]
        for i in range(0, len(full_text), child_size)
    ]
    children = [
        ChildChunk(
            child_id=f"{doc_id}-child-{idx}",
            parent_id=doc_id,
            text=child_text,
        )
        for idx, child_text in enumerate(child_texts)
    ]
    return ParentChunk(parent_id=doc_id, text=full_text, children=children)


def retrieve_context(
    query_child_id: str,
    parent_store: dict,
    child_to_parent: dict,
) -> str:
    """根据命中的 child_id 查出对应 ParentChunk 的完整文本。"""
    parent_id = child_to_parent[query_child_id]
    return parent_store[parent_id].text


if __name__ == "__main__":
    # ── 1. 构建 Parent-Child 结构（两篇文档）──────────────────────
    doc_text_001 = (
        "公司成立于2010年，专注于人工智能领域的研发与应用。"
        "标准工作时间为周一至周五，每天9:00-18:00，午休12:00-13:00。"
        "公司每月15日发放工资，提供五险一金、带薪年假、节日福利及年终奖金。"
        "员工应遵守职业道德，保护公司机密，禁止从事与公司利益相冲突的行为。"
        "年假：入职满1年可享受5天带薪年假，每增加1年增加1天，最多15天。"
    )
    doc_text_002 = (
        "公司配备完善的培训体系，新员工入职后需完成为期三天的岗前培训。"
        "技术团队每季度举办内部分享会，鼓励知识共享与创新实践。"
        "公司提供弹性福利积分，员工可自主选择健身、餐饮或交通补贴。"
        "远程办公政策：经主管审批后，每周最多可申请两天居家办公。"
    )

    parent_001 = build_parent_child_chunks(doc_id="doc-001", full_text=doc_text_001, child_size=20)
    parent_002 = build_parent_child_chunks(doc_id="doc-002", full_text=doc_text_002, child_size=20)

    for parent in (parent_001, parent_002):
        print(f"=== ParentChunk: {parent.parent_id} ===")
        print(f"text (前30字): {parent.text[:30]}…")
        print(f"子块数量     : {len(parent.children)}")
        for child in parent.children:
            print(f"  [{child.child_id}] {child.text}")
        print()

    # ── 2. 模拟索引：合并两篇文档的映射表 ────────────────────────
    parent_store: dict = {
        parent_001.parent_id: parent_001,
        parent_002.parent_id: parent_002,
    }
    child_to_parent: dict = {
        c.child_id: c.parent_id
        for parent in (parent_001, parent_002)
        for c in parent.children
    }

    # ── 3. 模拟检索：分别命中两篇文档的子块 ──────────────────────
    for hit_child, label in [
        (parent_001.children[2], "doc-001 命中"),
        (parent_002.children[1], "doc-002 命中"),
    ]:
        print(f"=== {label}: {hit_child.child_id} ===")
        print(f"子块文本: {hit_child.text}")
        context = retrieve_context(hit_child.child_id, parent_store, child_to_parent)
        print(f"完整 ParentChunk 文本 (前40字): {context[:40]}…\n")

