"""
在线问答 Step 2：LLM 生成器
拼装 Prompt（系统指令 + 检索上下文 + 用户问题）→ DeepSeek 生成答案
"""
import os
from typing import List, Tuple
from openai import OpenAI
from .chunker import Chunk


# ──────────────────────── Prompt 模板 ────────────────────────

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。
请严格根据下面提供的【参考资料】回答用户问题，不要编造参考资料中没有的内容。
如果参考资料中没有相关信息，请直接回答"根据现有资料，我无法回答该问题"。
回答要简洁、准确、有条理。"""

CONTEXT_TEMPLATE = """【参考资料】
{context}

【用户问题】
{question}"""


class Generator:
    """
    调用 DeepSeek LLM 生成最终答案
    model        : DeepSeek 模型名称
    temperature  : 生成温度，0 = 确定性输出
    show_sources : 是否在答案中附上引用来源
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        temperature: float = 0.1,
        show_sources: bool = True,
    ):
        self.model = model
        self.temperature = temperature
        self.show_sources = show_sources
        self.client = OpenAI(
            api_key=api_key or os.environ["DEEPSEEK_API_KEY"],
            base_url=base_url,
        )

    def generate(
        self,
        question: str,
        retrieved: List[Tuple[float, Chunk]],
    ) -> str:
        """
        retrieved : [(score, Chunk), ...] 来自 Retriever
        返回最终答案字符串（含可选来源引用）
        """
        if not retrieved:
            return "未能检索到相关资料，无法回答该问题。"

        # 拼装上下文
        context_parts = []
        for i, (score, chunk) in enumerate(retrieved, 1):
            context_parts.append(
                f"[{i}] 来源：{chunk.source}\n{chunk.text}"
            )
        context = "\n\n".join(context_parts)

        user_message = CONTEXT_TEMPLATE.format(
            context=context,
            question=question,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
        )

        answer = response.choices[0].message.content.strip()

        # 追加来源引用
        if self.show_sources:
            sources = list({chunk.source for _, chunk in retrieved})
            answer += "\n\n---\n**参考来源：**\n" + "\n".join(
                f"- {s}" for s in sources
            )

        return answer

    def generate_stream(
        self,
        question: str,
        retrieved: List[Tuple[float, Chunk]],
    ):
        """流式生成，yield 每个 token 片段（适合命令行实时打印）"""
        if not retrieved:
            yield "未能检索到相关资料，无法回答该问题。"
            return

        context_parts = []
        for i, (score, chunk) in enumerate(retrieved, 1):
            context_parts.append(f"[{i}] 来源：{chunk.source}\n{chunk.text}")
        context = "\n\n".join(context_parts)

        user_message = CONTEXT_TEMPLATE.format(
            context=context, question=question
        )

        stream = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            stream=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
