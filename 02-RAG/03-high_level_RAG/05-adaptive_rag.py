# =============================================================================
#  8.5 Adaptive RAG（自适应路由 RAG）
# =============================================================================
#
#  原理：用 LLM 分类器判断问题类型，一次路由到最合适的子管道，
#        避免对简单问题过度检索、对复杂问题检索不足。
#
#  与 Agentic RAG 的区别：
#    Adaptive  → 一次路由决策，分发到固定子管道（成本可控）
#    Agentic   → 多步循环决策，LLM 自主决定何时/如何检索
#
#       question
#          │
#          ▼
#       [LLM 路由分类器]
#          │
#    ┌─────┼─────────────┐
#    ▼     ▼             ▼
#  direct  single       multi
#  直接生成  FAISS单跳   拆分子问题多次检索后综合
#    │     │             │
#    └─────┴─────────────┘
#              ▼
#           最终答案
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

# ── 路由类型 ──────────────────────────────────────────────────────────────────

ROUTE_DIRECT = "direct"   # 寒暄 / 常识，无需检索
ROUTE_SINGLE = "single"   # 单一事实，一次向量检索即可
ROUTE_MULTI  = "multi"    # 多子问题 / 对比分析，需多次检索


# ── 语料库 + 向量索引 ─────────────────────────────────────────────────────────

CORPUS = [
    "公司成立于2010年，专注于人工智能领域的研发与应用。",
    "标准工作时间为周一至周五，每天9:00-18:00，午休12:00-13:00。",
    "公司每月15日发放工资，提供五险一金、带薪年假、节日福利及年终奖金。",
    "员工应遵守职业道德，保护公司机密，禁止从事与公司利益相冲突的行为。",
    "年假：入职满1年可享受5天带薪年假，最多15天。",
    "报销应提交发票原件及审批单，审批通过后方可打款。",
]

_embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
_corpus_emb = _embed_model.encode(CORPUS, normalize_embeddings=True).astype("float32")
_index = faiss.IndexFlatIP(_corpus_emb.shape[1])
_index.add(_corpus_emb)


def vector_search(query: str, top_k: int = 2) -> list[tuple[float, str]]:
    q_emb = _embed_model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = _index.search(q_emb, k=top_k)
    return [(float(scores[0][i]), CORPUS[indices[0][i]]) for i in range(top_k)]


# ── LLM 路由分类器 ────────────────────────────────────────────────────────────

def _parse_route(text: str) -> str:
    t = text.strip().lower()
    if "multi" in t or "多跳" in t or "复杂" in t:
        return ROUTE_MULTI
    if "single" in t or "单跳" in t or "检索" in t:
        return ROUTE_SINGLE
    if "direct" in t or "直接" in t:
        return ROUTE_DIRECT
    return ROUTE_SINGLE


def classify_question(llm: ChatDeepSeek, question: str) -> str:
    """
    LLM 零样本路由：判断应走哪条子管道。
    - direct：寒暄、与员工手册无关的常识问答
    - single：只涉及一个政策点（年假几天、几号发工资）
    - multi：  多个子问题、对比、综合分析
    """
    r = llm.invoke(
        f"你是 RAG 路由分类器。根据用户问题，选择最合适的处理管道：\n"
        f"- direct：寒暄或与员工手册无关，无需检索\n"
        f"- single：单一政策事实，一次检索即可（如年假天数、发薪日）\n"
        f"- multi：多个子问题、对比或综合分析（如同时问年假和工资、对比两项政策）\n\n"
        f"问题：{question}\n"
        f"只回答一个标签：direct / single / multi"
    )
    return _parse_route(r.content)


# ── 三条子管道 ────────────────────────────────────────────────────────────────

def generate_answer(llm: ChatDeepSeek, question: str, context: str = "") -> str:
    if context:
        prompt = (
            f"根据以下参考资料回答问题，不要编造资料中没有的内容。\n"
            f"参考资料：\n{context}\n\n问题：{question}"
        )
    else:
        prompt = f"请简洁回答：{question}"
    return llm.invoke(prompt).content.strip()


def pipeline_direct(question: str, llm: ChatDeepSeek) -> str:
    print("  管道：direct → LLM 直接生成（跳过检索）")
    return generate_answer(llm, question)


def pipeline_single(question: str, llm: ChatDeepSeek) -> str:
    print("  管道：single → FAISS 单跳检索")
    results = vector_search(question, top_k=2)
    for score, doc in results:
        print(f"    检索 (score={score:.3f}): {doc[:50]}...")

    if not results or results[0][0] < 0.35:
        print("    未找到足够相关的文档")
        return generate_answer(llm, question)

    context = "\n".join(doc for _, doc in results)
    return generate_answer(llm, question, context)


def _decompose_question(llm: ChatDeepSeek, question: str) -> list[str]:
    """将复杂问题拆成 2~3 个可独立检索的子问题。"""
    r = llm.invoke(
        f"将以下复杂问题拆成 2~3 个可独立检索的子问题，每行一个，不要编号。\n"
        f"问题：{question}"
    )
    sub_qs = [line.strip().lstrip("0123456789.-、)） ") for line in r.content.splitlines()]
    return [q for q in sub_qs if q][:3] or [question]


def pipeline_multi(question: str, llm: ChatDeepSeek) -> str:
    print("  管道：multi → 拆分子问题 + 多次 FAISS 检索")
    sub_questions = _decompose_question(llm, question)
    print(f"    子问题: {sub_questions}")

    contexts: list[str] = []
    for i, sub_q in enumerate(sub_questions, 1):
        results = vector_search(sub_q, top_k=1)
        if results and results[0][0] >= 0.35:
            score, doc = results[0]
            print(f"    子检索 {i} (score={score:.3f}): {doc[:50]}...")
            contexts.append(f"[{sub_q}] {doc}")
        else:
            print(f"    子检索 {i}: 未命中")

    if not contexts:
        return generate_answer(llm, question)

    combined = "\n".join(contexts)
    return generate_answer(llm, question, combined)


# ── Adaptive RAG 路由入口 ─────────────────────────────────────────────────────

def adaptive_rag(question: str, llm: ChatDeepSeek) -> str:
    print(f"问题：{question}")

    route = classify_question(llm, question)
    print(f"  路由分类 → {route}")

    if route == ROUTE_DIRECT:
        return pipeline_direct(question, llm)
    if route == ROUTE_SINGLE:
        return pipeline_single(question, llm)
    return pipeline_multi(question, llm)


# ── 演示 ──────────────────────────────────────────────────────────────────────

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

print("【Adaptive RAG】示例 1：寒暄（direct 路径）")
r1 = adaptive_rag("你好，你是谁？", llm)
print(f"最终答案：{r1}\n")

print("=" * 60)
print("【Adaptive RAG】示例 2：单一政策（single 路径）")
r2 = adaptive_rag("公司年假最多几天？", llm)
print(f"最终答案：{r2}\n")

print("=" * 60)
print("【Adaptive RAG】示例 3：多主题对比（multi 路径）")
r3 = adaptive_rag("年假和工资政策的区别是什么？", llm)
print(f"最终答案：{r3}")
