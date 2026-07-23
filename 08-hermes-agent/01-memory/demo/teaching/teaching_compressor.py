# =============================================================================
# 教学版 ContextCompressor
# 对照源码: hermes_src/agent/context_compressor.py
# =============================================================================
# 保留：切开 head/middle/tail、调 summarize_fn、SUMMARY_PREFIX 拼装。
# Prompt 宏 / 积木见 prompt_template.py。
# 省略：cooldown / tool prune / token-budget tail / 奇偶角色修复。
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from prompt_template import (
    COMPRESSED_SUMMARY_METADATA_KEY,
    SUMMARY_END_MARKER,
    SUMMARY_PREFIX,
    build_summarizer_prompt,
)


def estimate_tokens_rough(messages: List[dict]) -> int:
    """粗估对话大概占多少 token（不用真实 tokenizer）。

    规则很简单：大约 chars/4，每条消息再加一点开销。
    用来判断「超没超压缩阈值」，不要求精确。
    """
    total = 0
    for m in messages:
        c = m.get("content") or ""
        if isinstance(c, list):
            c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
        total += len(str(c)) // 4 + 8
    return total


def serialize_for_summary(turns: List[dict]) -> str:
    """把中间那段对话翻成纯文本，交给辅助模型做摘要。

    格式：每行 `role: content`，方便 summarizer 阅读。
    """
    lines = []
    for m in turns:
        c = m.get("content") or ""
        if isinstance(c, list):
            c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
        lines.append(f"{m.get('role')}: {c}")
    return "\n".join(lines)


@dataclass
class CompressResult:
    """一次压缩的结果：新 messages、是否真压缩了、前后 token、摘要原文等。"""

    messages: List[dict]
    did_compress: bool
    before_tokens: int
    after_tokens: int
    summary: str = ""
    summarizer_prompt: str = ""
    head: List[dict] | None = None
    middle: List[dict] | None = None
    tail: List[dict] | None = None


class TeachingContextCompressor:
    """教学版压缩机：切开对话 → 调 LLM 摘要 → 用 SUMMARY_PREFIX 拼回去。"""

    def __init__(
        self,
        summarize_fn: Callable[[str], str],
        threshold_percent: float = 0.50,
        protect_first_n: int = 1,
        protect_last_n: int = 2,
        context_length: int = 800,
    ):
        """记下压缩策略和「真正去调 LLM」的函数。

        summarize_fn: 收到完整摘要 prompt，返回摘要正文（demo 里是 DeepSeek）
        threshold_percent: 上下文用到百分之多少就触发压缩（相对 context_length）
        protect_first_n / protect_last_n: 头尾各留几条不压缩
        context_length: 假想的上下文窗口大小（教学里故意设小，保证能触发）
        """
        self.summarize_fn = summarize_fn
        self.threshold_percent = threshold_percent
        self.protect_first_n = protect_first_n
        self.protect_last_n = protect_last_n
        self.context_length = context_length
        self.threshold_tokens = int(context_length * threshold_percent)
        self.last_prompt_tokens = 0
        self._previous_summary = ""

    def should_compress(self, prompt_tokens: int | None = None) -> bool:
        """看当前 token 数有没有超过阈值，决定要不要压缩。

        True = 该压了；False = 还能撑，先别动历史。
        """
        tokens = prompt_tokens if prompt_tokens is not None else self.last_prompt_tokens
        return tokens >= self.threshold_tokens

    def compress(
        self,
        messages: List[dict],
        *,
        provider_hint: str = "",
        focus_topic: str = "",
        force: bool = False,
    ) -> CompressResult:
        """执行一次压缩：head 保留 + middle 变摘要 + tail 保留。

        步骤：
        1. 不够长 / 没超阈值 → 原样返回
        2. 切开 head / middle / tail
        3. middle 序列化，可选拼上 provider_hint（身份事实）
        4. 组 prompt，调 summarize_fn 拿摘要
        5. 用 SUMMARY_PREFIX + 摘要 + END 包成一条 user 消息插回去

        force=True 时跳过「是否超阈值」检查（preflight 已判定要压）。
        """
        before = estimate_tokens_rough(messages)

        if not force and before < self.threshold_tokens:
            return CompressResult(messages, False, before, before)

        need = self.protect_first_n + self.protect_last_n + 1
        if len(messages) <= need:
            return CompressResult(messages, False, before, before)

        head = messages[: self.protect_first_n]
        tail = messages[-self.protect_last_n :]
        middle = messages[self.protect_first_n : -self.protect_last_n]

        blob = serialize_for_summary(middle)
        if provider_hint:
            blob += f"\n\nExtra facts to preserve (from memory provider):\n{provider_hint}"

        prompt = build_summarizer_prompt(
            blob,
            previous_summary=self._previous_summary,
            focus_topic=focus_topic,
        )
        summary = self.summarize_fn(prompt)
        self._previous_summary = summary

        content = f"{SUMMARY_PREFIX}\n\n{summary}\n\n{SUMMARY_END_MARKER}"
        summary_msg = {
            "role": "user",
            "content": content,
            COMPRESSED_SUMMARY_METADATA_KEY: True,
        }
        new_messages = head + [summary_msg] + tail
        after = estimate_tokens_rough(new_messages)
        return CompressResult(
            new_messages,
            True,
            before,
            after,
            summary=summary,
            summarizer_prompt=prompt,
            head=head,
            middle=middle,
            tail=tail,
        )
