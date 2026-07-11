# =============================================================================
#  8.2 Agentic RAG（Agent 驱动的 RAG）
# =============================================================================
#
#  原理：由 Agent（LLM + Tools）自主决定何时检索、检索什么、是否继续检索，
#        把 RAG 从「固定一次检索」变为多步决策循环。
#
#  ── 核心流程 ─────────────────────────────────────────────────────────────────
#
#       question ──► LLM（Agent）──► 要检索吗？──否──► 直接回答
#                         │ 是
#                         ▼
#                  search_handbook（FAISS 向量检索）
#                         │
#                         ▼
#                  够了吗？──否──► 换关键词再搜（可多次）
#                     │ 是
#                     ▼
#                  最终答案
#
#  重点：检索次数、检索词由 LLM 决定，不是固定「问一次、搜一次」。
#
#  普通 RAG:  question → 检索 → LLM
#  Agentic:   question → LLM ⇄ 工具（0~N 次）→ 答案
#
#  依赖：
#    pip install langchain-deepseek sentence-transformers faiss-cpu python-dotenv
#  环境变量：
#    DEEPSEEK_API_KEY
#
# =============================================================================

import os
import sys

import faiss
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

# ── 语料库 + 向量索引（真实检索，非 mock）──────────────────────────────────────

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


def _vector_search(query: str, top_k: int = 2) -> list[tuple[float, str]]:
    q_emb = _embed_model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = _index.search(q_emb, k=top_k)
    return [(float(scores[0][i]), CORPUS[indices[0][i]]) for i in range(top_k)]


# ── Agent 工具 ────────────────────────────────────────────────────────────────

@tool
def search_handbook(query: str) -> str:
    """
    搜索公司员工手册知识库。
    用于查询年假、工资发放、工作时间、报销、职业道德等公司政策。
    输入应为与政策相关的检索关键词或问句。
    """
    results = _vector_search(query, top_k=2)
    if not results or results[0][0] < 0.3:
        return "未找到相关手册内容，请尝试换关键词或拆分问题后再次检索。"
    lines = [f"[相似度={score:.3f}] {doc}" for score, doc in results]
    return "\n".join(lines)


TOOLS = [search_handbook]

SYSTEM_PROMPT = """你是公司员工手册问答 Agent。
规则：
1. 涉及公司政策（年假、工资、工时、报销、保密等）时，必须先调用 search_handbook 检索，再回答。
2. 若一次检索不够，可换关键词多次调用 search_handbook。
3. 多子问题（如同时问年假和工资）应分别检索或一次用覆盖性关键词检索。
4. 仅当问题与手册无关（如寒暄）时，可直接回答，不必检索。
5. 回答必须基于检索结果，不要编造手册中没有的内容。"""


# ── 调试输出 ──────────────────────────────────────────────────────────────────

def _role_label(msg) -> str:
    return type(msg).__name__.replace("Message", "")


def _format_messages(messages) -> str:
    """将完整 messages 列表格式化为可读文本。"""
    blocks = []
    for msg in messages:
        block = [f"[{_role_label(msg)}]"]
        block.append(msg.content if msg.content else "(无文本内容)")
        if getattr(msg, "tool_calls", None):
            block.append("tool_calls:")
            for tc in msg.tool_calls:
                block.append(f"  - {tc['name']}({tc['args']})")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def _format_response(response) -> str:
    """将 Agent 响应格式化为可读文本（含 tool_calls）。"""
    parts = []
    if response.content:
        parts.append(response.content)
    if response.tool_calls:
        parts.append("tool_calls:")
        for tc in response.tool_calls:
            parts.append(f"  - {tc['name']}({tc['args']})")
    return "\n".join(parts) if parts else "(无文本内容，且无 tool_calls)"


# ── Agentic RAG 主循环 ────────────────────────────────────────────────────────

def agentic_rag(
    question: str,
    llm: ChatDeepSeek,
    max_steps: int = 5,
) -> str:
    """
    LLM 自主决策的工具调用循环：
    决定是否检索 → 调用 search_handbook → 评估是否足够 → 生成答案。
    """
    llm_with_tools = llm.bind_tools(TOOLS)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    for step in range(1, max_steps + 1):
        print(f"\n{'─' * 60}")
        print(f"Step {step} | Agent 决策: 是否需要检索？")
        print(f"{'─' * 60}")
        print(">>> 完整 Prompt（messages）:")
        print(_format_messages(messages))
        print(f"{'─' * 60}")
        response = llm_with_tools.invoke(messages)
        print("<<< 完整 Response:")
        print(_format_response(response))
        print(f"{'─' * 60}")
        messages.append(response)

        if not response.tool_calls:
            print(f"  Step {step} | Agent tools: 无需更多工具，生成最终答案")
            return response.content

        for tool_call in response.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            print(f"  Step {step} | 工具: {name}({args})")

            if name == "search_handbook":
                result = search_handbook.invoke(args)
            else:
                result = f"未知工具: {name}"

            print(f"           结果: {result[:80]}{'...' if len(result) > 80 else ''}")
            messages.append(
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            )

    # 达到步数上限，强制总结
    final = llm.invoke(
        messages
        + [HumanMessage(content="请根据已有检索结果给出最终答案，不要继续调用工具。")]
    )
    return final.content


# ── 演示 ──────────────────────────────────────────────────────────────────────

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# print("【Agentic RAG】示例 1：单主题政策问答")
# q1 = "公司年假最多几天？有什么享受条件？"
# print(f"问题：{q1}")
# answer1 = agentic_rag(q1, llm)
# print(f"最终答案：{answer1}\n")

print("=" * 60)
print("【Agentic RAG】示例 2：多主题需多次检索")
q2 = "公司几号发工资？报销需要什么材料？"
print(f"问题：{q2}")
answer2 = agentic_rag(q2, llm)
print(f"最终答案：{answer2}")
