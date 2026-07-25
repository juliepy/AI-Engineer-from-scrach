# =============================================================================
# DeepSeek LLM 接口（带 tools 的主模型调用）
# =============================================================================
# 对照 01-memory/demo/teaching/llm.py；本模块额外支持 tool_calls。
# =============================================================================
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, List, Optional

HERE = Path(__file__).resolve().parent  # .../demo/teaching
DEMO_ROOT = HERE.parent
REPO_ROOT = HERE.parents[3]  # AI_coding_interview/

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"

ChatWithToolsFn = Callable[..., Any]


_ENV_KEYS = ("DEEPSEEK_API_KEY", "TAVILY_API_KEY")


def load_dotenv_files() -> None:
    """查找顺序：demo/.env → 02-run-agent/.env → 01-memory/demo/.env → 仓库根 .env。

    会填充尚未在环境里的 DEEPSEEK_API_KEY / TAVILY_API_KEY。
    """
    missing = [k for k in _ENV_KEYS if not (os.getenv(k) or "").strip()]
    if not missing:
        return
    candidates = [
        DEMO_ROOT / ".env",
        DEMO_ROOT.parent / ".env",
        DEMO_ROOT.parent.parent / "01-memory" / "demo" / ".env",
        DEMO_ROOT.parent.parent / "01-memory" / ".env",
        REPO_ROOT / ".env",
    ]
    found: set[str] = set()
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                if key not in missing or key in found:
                    continue
                val = val.strip().strip("'").strip('"')
                if val:
                    os.environ[key] = val
                    found.add(key)
            if found.issuperset(missing):
                return
        except OSError:
            continue


def require_api_key() -> str:
    load_dotenv_files()
    api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit(
            "[fatal] 未找到 DEEPSEEK_API_KEY。\n"
            "  请在 demo/.env（或仓库根 .env）写入：\n"
            "    DEEPSEEK_API_KEY=sk-...\n"
            "  可选: TAVILY_API_KEY=tvly-...  （否则 web_search 用 ddgs）\n"
            "  获取: https://platform.deepseek.com/api_keys"
        )
    return api_key


def _to_assistant_namespace(message: Any) -> SimpleNamespace:
    """把 OpenAI SDK message 转成 conversation_loop 用的简单对象。"""
    tool_calls = []
    raw_tcs = getattr(message, "tool_calls", None) or []
    for tc in raw_tcs:
        fn = getattr(tc, "function", None)
        tool_calls.append(
            SimpleNamespace(
                id=getattr(tc, "id", None) or f"call_{len(tool_calls)}",
                function=SimpleNamespace(
                    name=getattr(fn, "name", "") if fn else "",
                    arguments=getattr(fn, "arguments", "{}") if fn else "{}",
                ),
            )
        )
    return SimpleNamespace(
        content=getattr(message, "content", None) or "",
        tool_calls=tool_calls or None,
    )


def make_chat_with_tools(api_key: str | None = None) -> ChatWithToolsFn:
    """造主循环用的 chat_with_tools(system, messages, tools) → assistant message。"""
    from openai import OpenAI

    key = (api_key or "").strip() or require_api_key()
    client = OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)

    def chat_with_tools(
        *,
        system: str,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
        tool_choice: str | None = "auto",
    ) -> SimpleNamespace:
        wire: List[dict] = [{"role": "system", "content": system}]
        for m in messages:
            role = m.get("role")
            if role == "assistant" and m.get("tool_calls"):
                wire.append(
                    {
                        "role": "assistant",
                        "content": m.get("content") or "",
                        "tool_calls": m["tool_calls"],
                    }
                )
            elif role == "tool":
                wire.append(
                    {
                        "role": "tool",
                        "tool_call_id": m.get("tool_call_id"),
                        "content": m.get("content") or "",
                        **({"name": m["name"]} if m.get("name") else {}),
                    }
                )
            else:
                wire.append(
                    {
                        "role": role,
                        "content": m.get("content") or "",
                    }
                )

        kwargs: dict = {
            "model": DEEPSEEK_MODEL,
            "messages": wire,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

        try:
            resp = client.chat.completions.create(**kwargs)
        except Exception as exc:
            raise SystemExit(
                f"[fatal] DeepSeek tool-loop call failed: {exc}\n"
                "  请检查 DEEPSEEK_API_KEY 是否有效\n"
                "  获取: https://platform.deepseek.com/api_keys"
            ) from exc

        choice = resp.choices[0]
        return _to_assistant_namespace(choice.message)

    return chat_with_tools


def format_tools_brief(tools: List[dict]) -> str:
    lines = []
    for t in tools:
        fn = t.get("function") or {}
        lines.append(f"- {fn.get('name')}: {(fn.get('description') or '')[:80]}")
    return "\n".join(lines)
