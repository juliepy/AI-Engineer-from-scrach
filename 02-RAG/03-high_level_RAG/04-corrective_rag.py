# =============================================================================
#  8.4 Corrective RAG（纠正性 RAG）
# =============================================================================
#
#  原理：检索后由评估器判断证据质量；不达标时改写查询并补充外部检索，
#        再精炼上下文，保证生成有可靠来源支撑。
#
#  ── 核心流程（对齐 CRAG 论文）──────────────────────────────────────────────
#
#       question
#          │
#          ▼
#       FAISS 向量检索 Top-K
#          │
#          ▼
#       [评估器] 判断检索质量 → correct / incorrect / ambiguous
#          │
#       ┌──┴────────────────────────────────────────┐
#       │ correct          incorrect    ambiguous   │
#       │    │                 │             │       │
#       │    ▼                 ▼             ▼       │
#       │ 直接用检索      改写查询+网页搜索   检索+网页  │
#       └──────┬─────────────────┬─────────────┘     │
#              │                 │                   │
#              ▼                 ▼                   │
#         知识精炼（LLM 提取相关片段）                  │
#              │                                     │
#              ▼                                     │
#           LLM 生成答案 ◄────────────────────────────┘
#
#  依赖：langchain-deepseek sentence-transformers faiss-cpu python-dotenv
#  环境变量：DEEPSEEK_API_KEY
#
# =============================================================================

import os
import sys

import faiss
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

RELEVANCE_THRESHOLD = 0.45  # 向量相似度下限，低于则倾向触发纠正

# ── 内部知识库 + 向量索引 ─────────────────────────────────────────────────────

CORPUS = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00，午休12:00-13:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假、节日福利及年终奖金。",
    "员工应遵守职业道德，保护公司机密，禁止从事与公司利益相冲突的行为。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
    "报销应提交发票原件及审批单，审批通过后方可打款。",
]

# 模拟外部网页知识（实际项目可替换为 Tavily / Bing Search API）
WEB_CORPUS = {
    "着装": "根据《员工仪容仪表规范》，工作日应着正装或商务休闲装，禁止穿拖鞋、背心进入办公区。",
    "考勤": "迟到30分钟以内记迟到一次；迟到超过30分钟按旷工半天处理。",
    "劳动合同": "根据《劳动合同法》，用人单位应按时足额支付劳动报酬，不得无故拖欠。",
    "保密": "涉密岗位员工离职后两年内仍负有保密义务，违约需承担法律责任。",
}

_embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
_corpus_emb = _embed_model.encode(CORPUS, normalize_embeddings=True).astype("float32")
_index = faiss.IndexFlatIP(_corpus_emb.shape[1])
_index.add(_corpus_emb)


def vector_search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    q_emb = _embed_model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = _index.search(q_emb, k=top_k)
    return [(float(scores[0][i]), CORPUS[indices[0][i]]) for i in range(top_k)]


# ── 检索质量评估（CRAG 中的 Retrieval Evaluator）──────────────────────────────

def _parse_label(text: str) -> str:
    t = text.strip().lower()
    if "incorrect" in t or "错误" in t or "不相关" in t:
        return "incorrect"
    if "ambiguous" in t or "模糊" in t or "部分" in t:
        return "ambiguous"
    return "correct"


def evaluate_retrieval(
    llm: ChatDeepSeek, question: str, results: list[tuple[float, str]]
) -> str:
    """
    综合向量分数 + LLM 判断，返回 correct / incorrect / ambiguous。
    """
    if not results or results[0][0] < RELEVANCE_THRESHOLD:
        return "incorrect"

    docs_text = "\n".join(f"- [{s:.3f}] {d}" for s, d in results)
    r = llm.invoke(
        f"你是检索质量评估器。根据问题和检索到的文档，判断证据是否足以回答问题。\n"
        f"问题：{question}\n"
        f"检索结果：\n{docs_text}\n\n"
        f"只回答以下三个标签之一：correct（完全相关）、ambiguous（部分相关）、incorrect（不相关）"
    )
    return _parse_label(r.content)


# ── 纠正动作：改写查询 + 网页搜索 ────────────────────────────────────────────

def rewrite_query(llm: ChatDeepSeek, question: str) -> str:
    r = llm.invoke(
        f"将以下用户问题改写为适合搜索引擎的简洁关键词（不超过15字）。\n"
        f"问题：{question}\n"
        f"只输出改写后的查询，不要解释。"
    )
    return r.content.strip()


def web_search(query: str) -> str:
    """模拟网页搜索：按关键词匹配外部语料，未命中则返回通用劳动法条款。"""
    for keyword, content in WEB_CORPUS.items():
        if keyword in query:
            return f"（网页检索）{content}"
    return (
        f"（网页检索）关于「{query}」："
        "可参考《劳动合同法》及行业通用员工管理规范，建议查阅公司最新公示制度。"
    )


def refine_knowledge(llm: ChatDeepSeek, question: str, raw_context: str) -> str:
    """知识精炼：从原始上下文中提取与问题相关的片段，去除噪声。"""
    r = llm.invoke(
        f"从以下资料中提取与问题直接相关的句子，去掉无关内容。若无相关内容，回答「无」。\n"
        f"问题：{question}\n"
        f"资料：\n{raw_context}\n\n"
        f"只输出精炼后的要点，每条一行。"
    )
    refined = r.content.strip()
    return refined if refined and refined != "无" else raw_context


def generate_answer(llm: ChatDeepSeek, question: str, context: str) -> str:
    return llm.invoke(
        f"根据以下参考资料回答问题。资料不足时请明确说明，不要编造。\n"
        f"参考资料：\n{context}\n\n问题：{question}"
    ).content.strip()


# ── Corrective RAG 主流程 ─────────────────────────────────────────────────────

def corrective_rag(question: str, llm: ChatDeepSeek) -> str:
    print(f"问题：{question}")

    # ① 向量检索
    results = vector_search(question, top_k=3)
    for score, doc in results:
        print(f"  检索 (score={score:.3f}): {doc[:50]}...")

    # ② 评估检索质量
    verdict = evaluate_retrieval(llm, question, results)
    print(f"  [评估器] 检索质量 → {verdict}")

    # ③ 按评估结果选择纠正策略
    retrieved_ctx = "\n".join(doc for _, doc in results)

    if verdict == "correct":
        print("  策略：证据充足，直接使用检索结果")
        raw_context = retrieved_ctx

    elif verdict == "incorrect":
        print(f"  策略：证据不足（score < {RELEVANCE_THRESHOLD} 或评估为 incorrect）→ 触发纠正")
        new_query = rewrite_query(llm, question)
        print(f"  改写查询: {new_query}")
        web_ctx = web_search(new_query)
        print(f"  {web_ctx}")
        raw_context = web_ctx

    else:  # ambiguous
        print("  策略：部分相关 → 检索结果 + 网页搜索合并")
        new_query = rewrite_query(llm, question)
        print(f"  改写查询: {new_query}")
        web_ctx = web_search(new_query)
        print(f"  {web_ctx}")
        raw_context = retrieved_ctx + "\n" + web_ctx

    # ④ 知识精炼
    context = refine_knowledge(llm, question, raw_context)
    print(f"  精炼上下文: {context[:80]}...")

    # ⑤ 生成答案
    answer = generate_answer(llm, question, context)
    return answer


# ── 演示 ──────────────────────────────────────────────────────────────────────

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

print("【Corrective RAG】示例 1：内部手册可回答（correct 路径）")
r1 = corrective_rag("公司工资什么时候发放？", llm)
print(f"最终答案：{r1}\n")

print("=" * 60)
print("【Corrective RAG】示例 2：手册无覆盖，触发网页纠正（incorrect 路径）")
r2 = corrective_rag("公司员工着装有什么要求？", llm)
print(f"最终答案：{r2}")
