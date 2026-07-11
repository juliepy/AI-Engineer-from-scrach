# =============================================================================
#  8.1 GraphRAG（基于知识图谱的 RAG）
# =============================================================================
#
#  原理：从文本抽取实体与关系构建图，检索时沿子图或社区摘要获取证据。
#  适合：多跳关系推理、全局问题（"整体主题是什么"）。
#
#  ── 离线建图流程（索引阶段，对应 Step 1-2）────────────────────────────────────
#
#       原始文本 RAW_TEXT
#              │
#              ▼
#       RecursiveCharacterTextSplitter
#              │
#              ▼
#       chunks[] ──► Document(page_content=chunk)
#              │
#              ▼
#       LLMGraphTransformer.convert_to_graph_documents()
#              │  DeepSeek 逐 chunk 抽取 nodes + relationships
#              ▼
#       GraphDocument[]
#         ├─ nodes:      [Node(id="带薪年假"), ...]
#         ├─ relationships: [带薪年假 --[上限]--> 最多15天, ...]
#         └─ source:     原始 chunk（可追溯）
#              │
#              ▼
#       ingest_graph_documents() → SimpleKG.edges（邻接表）
#
#  ── 在线搜索流程（检索阶段，对应 graph_rag_search）────────────────────────────
#
#       用户问题 question: "年假最多几天？"
#              │
#              ▼
#       ┌──────────────────────────────────────────┐
#       │ Step A: 种子实体定位 extract_seed_entity │
#       │   all_entities() → 图谱全部实体列表      │
#       │   LLM 从列表中选核心主题实体              │
#       │   find_entity() → 名称对齐               │
#       │   resolve_seed_entity() → 叶子回退父节点  │
#       └──────────────────┬───────────────────────┘
#                          │ 种子实体: "带薪年假"
#                          ▼
#       ┌──────────────────────────────────────────┐
#       │ Step B: 子图检索 subgraph(hops=2)        │
#       │   BFS 从种子实体出发，逐跳扩展出边          │
#       │                                          │
#       │   queue = [带薪年假]                      │
#       │      │ 第1跳                              │
#       │      ├─ 带薪年假 --[包含]--> 5天带薪年假   │
#       │      └─ 带薪年假 --[上限]--> 最多15天  ✓   │
#       │      │ 第2跳（扩展客体，若无出边则结束）    │
#       │      ▼                                   │
#       │   返回三元组列表 + source 来源句           │
#       └──────────────────┬───────────────────────┘
#                          │ context（子图证据）
#                          ▼
#       ┌──────────────────────────────────────────┐
#       │ Step C: LLM 生成答案                      │
#       │   prompt = 知识图谱上下文 + question      │
#       │   → "带薪年假的上限为最多15天"            │
#       └──────────────────────────────────────────┘
#
#  ── 向量 RAG vs GraphRAG 对比 ───────────────────────────────────────────────
#
#       向量 RAG:  question → embedding → Top-K 相似 chunk → LLM
#       GraphRAG:  question → 实体定位 → BFS 子图 → 三元组上下文 → LLM
#
#  ┌──────────────┬────────────────────────────┬────────────────────────────┐
#  │    维度      │         向量 RAG            │         GraphRAG           │
#  ├──────────────┼────────────────────────────┼────────────────────────────┤
#  │ 检索依据     │ 语义相似度（向量距离）       │ 实体关系 + 图上游走（BFS）   │
#  │ 索引成本     │ 低：embed + 向量库即可      │ 高：LLM 逐 chunk 抽三元组建图 │
#  │ 检索延迟     │ 低：毫秒级 ANN 检索         │ 中高：实体定位 LLM + 子图遍历 │
#  │ 上下文形态   │ 原始文本块                  │ 结构化三元组 + 来源句        │
#  ├──────────────┼────────────────────────────┼────────────────────────────┤
#  │ 优点         │ 实现简单、速度快、泛化好     │ 多跳推理强、关系清晰可追溯   │
#  │              │ 对新文档增量索引容易         │ 跨 chunk 关联也能连通        │
#  │              │ 适合开放域语义匹配           │ 全局/主题类问题可扩展社区摘要 │
#  ├──────────────┼────────────────────────────┼────────────────────────────┤
#  │ 缺点         │ 弱于关系推理与多跳问答       │ 建图成本高、抽取质量依赖 LLM │
#  │              │ 相似块可能内容重复           │ 实体命名不一致需对齐         │
#  │              │ 跨段落因果/约束难串联        │ 开放域泛化不如向量检索灵活   │
#  ├──────────────┼────────────────────────────┼────────────────────────────┤
#  │ 擅长问题     │ 「哪段话和问题最像？」       │ 「A 和 B 什么关系？」        │
#  │              │ 「介绍一下 X」              │ 「X 的上限/条件/流程是什么？」│
#  │              │ 语义模糊匹配                │ 多跳：「A→B→C 能推出什么？」  │
#  ├──────────────┼────────────────────────────┼────────────────────────────┤
#  │ 本示例表现   │ 可能召回整段福利文本         │ 精准命中 带薪年假--[上限]-->15天│
#  └──────────────┴────────────────────────────┴────────────────────────────┘
#
#  选型建议：
#    - 文档问答、语义搜索、成本敏感        → 向量 RAG（或 + BM25 混合检索）
#    - 关系密集、制度规则、多跳推理        → GraphRAG
#    - 生产最佳实践                      → 向量召回 Top-K + 图谱子图 融合上下文
#
#  依赖：
#    pip install langchain-experimental langchain-deepseek langchain-text-splitters python-dotenv
#  环境变量：
#    DEEPSEEK_API_KEY（https://platform.deepseek.com/）
#
# =============================================================================

import os
import sys
from collections import defaultdict

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_deepseek import ChatDeepSeek
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


# ── 简易知识图谱（邻接表）────────────────────────────────────────────────────

class SimpleKG:
    def __init__(self):
        # edges: {实体: [(关系, 目标实体, 来源句)]}
        self.edges: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    def add_triple(self, subject: str, relation: str, obj: str, source: str = ""):
        triple = (relation, obj, source)
        if triple not in self.edges[subject]:
            self.edges[subject].append(triple)

    def ingest_graph_documents(self, graph_documents: list) -> int:
        """将 LLMGraphTransformer 输出的 GraphDocument 写入邻接表。"""
        count = 0
        for graph_doc in graph_documents:
            source = graph_doc.source.page_content
            for rel in graph_doc.relationships:
                subject = str(rel.source.id)
                relation = rel.type
                obj = str(rel.target.id)
                before = len(self.edges[subject])
                self.add_triple(subject, relation, obj, source=source)
                if len(self.edges[subject]) > before:
                    count += 1
        return count

    def all_entities(self) -> set[str]:
        entities = set(self.edges.keys())
        for edge_list in self.edges.values():
            for _, obj, _ in edge_list:
                entities.add(obj)
        return entities

    def find_entity(self, keyword: str) -> str | None:
        """在图谱实体中模糊匹配种子实体。"""
        if keyword in self.all_entities():
            return keyword
        for entity in self.all_entities():
            if keyword in entity or entity in keyword:
                return entity
        return None

    def subjects_of(self, entity: str) -> list[str]:
        """查找以 entity 为客体的所有主体（逆向边）。"""
        return [
            subject
            for subject, edges in self.edges.items()
            if any(obj == entity for _, obj, _ in edges)
        ]

    def resolve_seed_entity(self, entity: str) -> str:
        """
        确保种子实体可作为 BFS 起点。
        若命中叶子节点（无出边），回退到其父主体。
        """
        if entity in self.edges and self.edges[entity]:
            return entity
        parents = self.subjects_of(entity)
        return parents[0] if parents else entity

    def subgraph(self, entity: str, hops: int = 2) -> list[str]:
        """BFS 获取 entity 出发 hops 步内的所有三元组描述。"""
        visited, queue, results = set(), [entity], []
        for _ in range(hops):
            next_q = []
            for node in queue:
                if node in visited:
                    continue
                visited.add(node)
                for rel, obj, src in self.edges.get(node, []):
                    results.append(f"{node} --[{rel}]--> {obj}  ({src})")
                    next_q.append(obj)
            queue = next_q
        return results


def extract_seed_entity(question: str, kg: SimpleKG, llm: ChatDeepSeek) -> str | None:
    """
    从用户问题中提取种子实体，并与图谱已有实体对齐。
    优先 LLM 在实体列表中选最相关项；失败则回退到模糊匹配。
    """
    entities = sorted(kg.all_entities())
    if not entities:
        return None

    response = llm.invoke(
        "你是知识图谱检索助手。根据用户问题，从下列实体中选择最适合作为子图遍历起点的"
        "**核心主题实体**（如政策、福利、组织、人物等概念），"
        "不要选择具体数值、日期、天数等属性值。"
        "只返回实体名称本身，不要解释。\n"
        f"可选实体：{entities}\n"
        f"用户问题：{question}\n"
        "种子实体："
    )
    candidate = response.content.strip().strip("'\"")

    if matched := kg.find_entity(candidate):
        return kg.resolve_seed_entity(matched)

    # 回退：用问题原文做模糊匹配（如「年假最多几天」→「带薪年假」）
    if matched := kg.find_entity(question):
        return kg.resolve_seed_entity(matched)

    return None


def build_kg_from_chunks(
    chunks: list[str],
    transformer: LLMGraphTransformer,
) -> tuple[SimpleKG, list]:
    """chunks → Document → LLMGraphTransformer → SimpleKG。"""
    documents = [Document(page_content=chunk) for chunk in chunks]
    graph_documents = transformer.convert_to_graph_documents(documents)
    kg = SimpleKG()
    kg.ingest_graph_documents(graph_documents)
    return kg, graph_documents


def graph_rag_search(
    question: str,
    kg: SimpleKG,
    llm: ChatDeepSeek,
    hops: int = 2,
) -> dict:
    """
    知识图谱搜索完整流程：种子实体定位 → BFS 子图检索 → LLM 生成答案。

    返回:
        seed_entity: 种子实体
        context:     子图三元组列表
        answer:      LLM 答案（无上下文时为 None）
    """
    seed_entity = extract_seed_entity(question, kg, llm)
    context = kg.subgraph(seed_entity, hops=hops) if seed_entity else []
    answer = None
    if context:
        response = llm.invoke(
            f"根据以下知识图谱回答问题，不要编造图谱中没有的内容：\n"
            f"{chr(10).join(context)}\n\n问题：{question}"
        )
        answer = response.content
    return {"seed_entity": seed_entity, "context": context, "answer": answer}


# ── Step 1: 文本分块 ──────────────────────────────────────────────────────────

RAW_TEXT = (
    "第一段：公司成立于2010年，专注于人工智能领域的研发与应用。\n\n"
    "第二段：标准工作时间为周一至周五，每天9:00-18:00，午休12:00-13:00。"
    "公司每月15日发放工资，提供五险一金、带薪年假、节日福利及年终奖金。"
    "入职满1年可享受5天带薪年假，最多15天。\n\n"
    "第三段：员工应遵守职业道德，保护公司机密，禁止从事与公司利益相冲突的行为。"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=120,
    chunk_overlap=10,
    separators=["\n\n", "\n", "。", ""],
)
chunks = splitter.split_text(RAW_TEXT)

print("【Step 1】Text Splitter 分块结果")
for i, chunk in enumerate(chunks):
    print(f"  chunk-{i}: {chunk}")


# ── Step 2: LLMGraphTransformer 抽取三元组 ────────────────────────────────────

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# allowed_nodes / allowed_relationships 可约束 schema；留空则由 LLM 自由抽取
llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["公司", "员工", "组织", "人物", "政策", "福利", "时间"],
    strict_mode=False,
)

print("\n【Step 2】LLMGraphTransformer 抽取实体与关系（调用 DeepSeek API）...")
kg, graph_documents = build_kg_from_chunks(chunks, llm_transformer)

for i, graph_doc in enumerate(graph_documents):
    print(f"\n  chunk-{i} 抽取结果:")
    print(f"    nodes: {[n.id for n in graph_doc.nodes]}")
    for rel in graph_doc.relationships:
        print(f"    {rel.source.id} --[{rel.type}]--> {rel.target.id}")

print(f"\n  共写入 {sum(len(v) for v in kg.edges.values())} 条边")
for subject, edges in kg.edges.items():
    for rel, obj, src in edges:
        print(f"  {subject} --[{rel}]--> {obj}  ← {src[:30]}...")


# ── Step 3: 知识图谱搜索（种子实体 → 子图检索 → 生成答案）────────────────────

question = "年假最多几天？"
result = graph_rag_search(question, kg, llm, hops=2)

print(f"\n【Step 3-A】种子实体定位")
print(f"  问题: {question}")
print(f"  种子实体: {result['seed_entity']}")

print(f"\n【Step 3-B】BFS 子图检索")
if result["context"]:
    for triple in result["context"]:
        print(f"  {triple}")
else:
    print("  未命中子图，请检查实体抽取或图谱构建结果")
    print(f"  当前图谱实体: {sorted(kg.all_entities())}")

if result["answer"]:
    print(f"\n【Step 3-C】LLM 生成答案")
    print(f"  {result['answer']}")
