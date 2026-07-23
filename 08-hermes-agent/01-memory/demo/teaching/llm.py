# =============================================================================
# DeepSeek LLM 接口（辅助压缩 + 主模型）
# =============================================================================
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, List, Tuple

HERE = Path(__file__).resolve().parent  # .../demo/teaching
DEMO_ROOT = HERE.parent
REPO_ROOT = HERE.parents[3]  # AI_coding_interview/

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"

SummarizeFn = Callable[[str], str]
MainChatFn = Callable[[str, List[dict]], str]


def load_dotenv_files() -> None:
    """从附近的 .env 文件里读 DEEPSEEK_API_KEY（环境变量里已有就不动）。

    查找顺序：demo/.env → 01-memory/.env → notebooks/.env → 仓库根 .env。
    找到第一个有效 key 就写入 os.environ 并返回。
    """
    if (os.getenv("DEEPSEEK_API_KEY") or "").strip():
        return
    candidates = [
        DEMO_ROOT / ".env",
        DEMO_ROOT.parent / ".env",
        DEMO_ROOT.parent / "notebooks" / ".env",
        REPO_ROOT / ".env",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                if key.strip() != "DEEPSEEK_API_KEY":
                    continue
                val = val.strip().strip("'").strip('"')
                if val:
                    os.environ["DEEPSEEK_API_KEY"] = val
                    return
        except OSError:
            continue


def require_api_key() -> str:
    """拿到可用的 DeepSeek API Key；没有就直接退出并提示怎么配。"""
    api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        load_dotenv_files()
        api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit(
            "[fatal] 未找到 DEEPSEEK_API_KEY。\n"
            "  请在 demo/.env（或 notebooks/.env / 仓库根 .env）写入：\n"
            "    DEEPSEEK_API_KEY=sk-...\n"
            "  获取: https://platform.deepseek.com/api_keys"
        )
    return api_key


def make_llm(api_key: str | None = None) -> Tuple[SummarizeFn, MainChatFn]:
    """造两个调用函数：辅助压缩用的 summarize_fn，主对话用的 main_chat_fn。

    都走同一个 DeepSeek client。
    没传 api_key 时会自动 require_api_key()。
    """
    from openai import OpenAI

    key = (api_key or "").strip() or require_api_key()
    client = OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)

    def summarize_fn(prompt: str) -> str:
        """辅助模型：把压缩 prompt 发给 DeepSeek，拿回摘要正文。"""
        try:
            resp = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        except Exception as exc:
            raise SystemExit(
                f"[fatal] DeepSeek compression call failed: {exc}\n"
                "  请检查 demo/.env 中的 DEEPSEEK_API_KEY 是否有效\n"
                "  获取: https://platform.deepseek.com/api_keys"
            ) from exc
        return (resp.choices[0].message.content or "").strip()

    def main_chat_fn(system: str, messages: list[dict]) -> str:
        """主模型：带上 system +（可能已压缩的）messages，拿最终回复。"""
        wire = [
            {"role": m["role"], "content": m.get("content") or ""}
            for m in messages
        ]
        payload = [{"role": "system", "content": system}] + wire
        try:
            resp = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=payload,
                temperature=0.3,
            )
        except Exception as exc:
            raise SystemExit(
                f"[fatal] DeepSeek main call failed: {exc}\n"
                "  请检查 DEEPSEEK_API_KEY 是否有效"
            ) from exc
        return (resp.choices[0].message.content or "").strip()

    return summarize_fn, main_chat_fn
