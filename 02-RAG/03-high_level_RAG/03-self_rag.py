# =============================================================================
#  8.3 Self-RAG（自我反思的 RAG）
# =============================================================================
#
#  原理：生成前/后由 LLM 做四步自我反思（论文称 reflection tokens）：
#        Retrieve? → IsRel? → IsSup? → IsUse?
#
#  ── 核心流程 ─────────────────────────────────────────────────────────────────
#
#  整体思路：不盲目检索、不盲信检索结果。每一步都由 LLM 做一次「是/否」自省，
#  只有当前环节通过，才进入下一步；任一环节失败则走对应补救分支。
#
#  四步自省（论文称 reflection tokens）：
#
#    ① Retrieve? — 这个问题需要查资料吗？
#       · 否 → 跳过检索，直接用 LLM 生成（如寒暄、常识题）
#       · 是 → 进入向量检索
#
#    ② IsRel? — 检索到的文档真的和问题相关吗？
#       · 按相似度从高到低逐条检验
#       · 否 → 换下一条候选文档，直到找到相关文档或全部淘汰
#       · 全部不相关 → 返回「无法回答」
#
#    ③ IsSup? — 生成的答案是否完全有文档依据、没有编造？
#       · 否 → 带着「严格复述文档」的约束重新生成
#       · 是 → 进入下一步
#
#    ④ IsUse? — 答案是否完整、清晰地回答了问题？
#       · 否 → 基于同一文档再生成一次
#       · 是 → 输出为最终答案
#
#  流程图：
#
#       question
#          │
#       [Retrieve?] 要不要检索？ ──否──► 直接生成 → 最终答案
#          │ 是
#          ▼
#       FAISS 向量检索（取 top-k 候选）
#          │
#       [IsRel?]  文档相关吗？ ──否──► 换下一条文档（循环）
#          │ 是
#          ▼
#       基于该文档生成候选答案
#          │
#       [IsSup?]  有文档依据吗？ ──否──► 强调「勿编造」后重生成
#          │ 是
#          ▼
#       [IsUse?]  答案好用吗？ ──否──► 重新生成
#          │ 是
#          ▼
#        最终答案
#
#  对比 Agentic RAG：Self-RAG 重点是「检索质量 + 答案质量」的自省，而非多工具编排。
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


def vector_search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    q_emb = _embed_model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = _index.search(q_emb, k=top_k)
    return [(float(scores[0][i]), CORPUS[indices[0][i]]) for i in range(top_k)]


# ── LLM 反思判断（替代论文中的 reflection tokens）────────────────────────────

def _parse_yes(text: str) -> bool:
    t = text.strip().lower()
    return t.startswith("是") or t == "yes" or "yes" in t.split()


def reflect_retrieve(llm: ChatDeepSeek, question: str) -> bool:
    """[Retrieve?] 是否需要检索文档。"""
    r = llm.invoke(
        f"判断以下问题是否需要查阅公司员工手册才能准确回答。\n"
        f"问题：{question}\n"
        f"只回答一个字：是 或 否"
    )
    return _parse_yes(r.content)


def reflect_relevant(llm: ChatDeepSeek, question: str, doc: str) -> bool:
    """[IsRel?] 检索文档是否与问题相关。"""
    r = llm.invoke(
        f"判断以下文档是否有助于回答问题。\n"
        f"问题：{question}\n"
        f"文档：{doc}\n"
        f"只回答一个字：是 或 否"
    )
    return _parse_yes(r.content)


def reflect_supported(llm: ChatDeepSeek, doc: str, answer: str) -> bool:
    """[IsSup?] 答案是否有文档依据。"""
    r = llm.invoke(
        f"判断以下答案是否完全基于文档内容，没有编造。\n"
        f"文档：{doc}\n"
        f"答案：{answer}\n"
        f"只回答一个字：是 或 否"
    )
    return _parse_yes(r.content)


def reflect_useful(llm: ChatDeepSeek, question: str, answer: str) -> bool:
    """[IsUse?] 答案是否完整有用。"""
    r = llm.invoke(
        f"判断以下答案是否完整、清晰地回答了问题。\n"
        f"问题：{question}\n"
        f"答案：{answer}\n"
        f"只回答一个字：是 或 否"
    )
    return _parse_yes(r.content)


def generate_answer(llm: ChatDeepSeek, question: str, doc: str = "") -> str:
    if doc:
        prompt = (
            f"根据以下参考资料回答问题，不要编造资料中没有的内容。\n"
            f"参考资料：{doc}\n\n问题：{question}"
        )
    else:
        prompt = f"请回答：{question}"
    return llm.invoke(prompt).content.strip()


# ── Self-RAG 主流程 ───────────────────────────────────────────────────────────

def self_rag(question: str, llm: ChatDeepSeek) -> str:
    print(f"问题：{question}")

    # ① Retrieve?
    if not reflect_retrieve(llm, question):
        print("  [Retrieve?] 否 → 直接生成")
        return generate_answer(llm, question)

    print("  [Retrieve?] 是 → FAISS 向量检索")
    candidates = vector_search(question, top_k=3)

    # ② IsRel? — 逐条检验，取第一条相关文档
    doc = ""
    for score, text in candidates:
        print(f"  候选文档 (score={score:.3f}): {text[:40]}...")
        if reflect_relevant(llm, question, text):
            doc = text
            print(f"  [IsRel?] 是 → 采用该文档")
            break
        print("  [IsRel?] 否 → 换下一条")

    if not doc:
        print("  无相关文档，无法回答")
        return "根据现有资料，无法回答该问题。"

    # 生成候选答案
    answer = generate_answer(llm, question, doc)

    # ③ IsSup?
    if not reflect_supported(llm, doc, answer):
        print("  [IsSup?] 否 → 重新生成（强调基于文档）")
        answer = generate_answer(
            llm, question,
            doc + "\n（请严格复述文档中的事实，不要添加文档以外的信息）",
        )
    else:
        print("  [IsSup?] 是 → 答案有文档支撑")

    # ④ IsUse?
    if not reflect_useful(llm, question, answer):
        print("  [IsUse?] 否 → 重新生成")
        answer = generate_answer(llm, question, doc)
    else:
        print("  [IsUse?] 是 → 输出最终答案")

    return answer


# ── 演示 ──────────────────────────────────────────────────────────────────────

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

print("【Self-RAG】示例 1：事实性问题（需检索）")
r1 = self_rag("公司年假最多几天？", llm)
print(f"最终答案：{r1}\n")

print("=" * 60)
print("【Self-RAG】示例 2：寒暄（无需检索）")
r2 = self_rag("你好，你是谁？", llm)
print(f"最终答案：{r2}")
