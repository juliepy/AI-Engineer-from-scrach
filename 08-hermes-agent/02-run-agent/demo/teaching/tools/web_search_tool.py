# =============================================================================
# web_search — 对照 hermes_src/tools/web_tools.py · WEB_SEARCH_SCHEMA / web_search_tool
# =============================================================================
# 保留：同名 schema、返回 JSON 形状 {success, data.web[{title,url,description,position}]}
# 后端（教学精简）：
#   1. 若有 TAVILY_API_KEY → Tavily（与 Hermes tavily backend 对齐）
#   2. 否则 DDGS / DuckDuckGo（Hermes ddgs backend，免 key）
# 省略：Firecrawl / Exa / Parallel / plugin registry 调度
# =============================================================================
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from registry import registry, tool_error


WEB_SEARCH_SCHEMA = {
    "name": "web_search",
    "description": (
        "Search the web for information. Returns up to 5 results by default with "
        "titles, URLs, and descriptions. The query is passed through to the "
        "configured backend, so operators such as site:domain, filetype:pdf, "
        "intitle:word, -term, and \"exact phrase\" may work when the backend supports them."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The search query to look up on the web. You may include "
                    "backend-supported operators such as site:example.com, "
                    "filetype:pdf, intitle:word, -term, or \"exact phrase\"."
                ),
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return. Defaults to 5.",
                "minimum": 1,
                "maximum": 10,
                "default": 5,
            },
        },
        "required": ["query"],
    },
}


def _normalize_limit(limit: Any) -> int:
    try:
        n = int(limit)
    except (TypeError, ValueError):
        n = 5
    return min(max(n, 1), 10)


def _pack_results(rows: List[Dict[str, Any]], *, backend: str) -> str:
    web = []
    for i, row in enumerate(rows, start=1):
        title = (row.get("title") or "").strip()
        url = (row.get("url") or row.get("href") or "").strip()
        description = (
            row.get("description")
            or row.get("body")
            or row.get("content")
            or ""
        )
        description = str(description).strip()
        if not title and not url and not description:
            continue
        web.append(
            {
                "title": title,
                "url": url,
                "description": description,
                "position": len(web) + 1,
            }
        )
    return json.dumps(
        {
            "success": True,
            "data": {"web": web},
            "_metadata": {"backend": backend},
        },
        ensure_ascii=False,
        indent=2,
    )


def _search_tavily(query: str, limit: int) -> Optional[str]:
    api_key = (os.getenv("TAVILY_API_KEY") or "").strip()
    if not api_key:
        return None
    payload = json.dumps(
        {
            "api_key": api_key,
            "query": query,
            "max_results": limit,
            "search_depth": "basic",
            "include_answer": False,
        }
    ).encode("utf-8")
    req = Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    rows = []
    for item in data.get("results") or []:
        rows.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "description": item.get("content"),
            }
        )
    return _pack_results(rows[:limit], backend="tavily")


def _search_ddgs(query: str, limit: int) -> Optional[str]:
    """Hermes ddgs backend：``ddgs`` 包（免 API Key）。"""
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # older package name
        except ImportError:
            return None
    rows = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=limit):
            rows.append(
                {
                    "title": item.get("title"),
                    "url": item.get("href") or item.get("link"),
                    "description": item.get("body"),
                }
            )
    return _pack_results(rows[:limit], backend="ddgs")


def _search_duckduckgo_html(query: str, limit: int) -> str:
    """最后兜底：DuckDuckGo Instant Answer API（结果较少，但零依赖）。"""
    url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
    req = Request(url, headers={"User-Agent": "hermes-teaching-demo/1.0"})
    with urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    rows: List[Dict[str, Any]] = []
    if data.get("AbstractText"):
        rows.append(
            {
                "title": data.get("Heading") or query,
                "url": data.get("AbstractURL") or "",
                "description": data.get("AbstractText"),
            }
        )
    for topic in data.get("RelatedTopics") or []:
        if len(rows) >= limit:
            break
        if isinstance(topic, dict) and topic.get("Text"):
            rows.append(
                {
                    "title": (topic.get("Text") or "")[:80],
                    "url": topic.get("FirstURL") or "",
                    "description": topic.get("Text") or "",
                }
            )
        elif isinstance(topic, dict) and topic.get("Topics"):
            for sub in topic["Topics"]:
                if len(rows) >= limit:
                    break
                if isinstance(sub, dict) and sub.get("Text"):
                    rows.append(
                        {
                            "title": (sub.get("Text") or "")[:80],
                            "url": sub.get("FirstURL") or "",
                            "description": sub.get("Text") or "",
                        }
                    )
    if not rows:
        return tool_error(
            "web_search returned no results. Install `ddgs` "
            "(`pip install ddgs`) or set TAVILY_API_KEY for a real backend."
        )
    return _pack_results(rows[:limit], backend="duckduckgo-instant")


def web_search_tool(query: str, limit: int = 5) -> str:
    """Search the web. Returns JSON string（形状对齐 Hermes web_search_tool）。"""
    q = (query or "").strip()
    if not q:
        return tool_error("query is required")
    limit = _normalize_limit(limit)
    try:
        result = _search_tavily(q, limit)
        if result is not None:
            return result
        result = _search_ddgs(q, limit)
        if result is not None:
            return result
        return _search_duckduckgo_html(q, limit)
    except Exception as exc:
        return tool_error(f"Error searching web: {exc}")


def check_web_search_requirements() -> bool:
    """对照 check_web_api_key：有任一可用后端即暴露工具。"""
    if (os.getenv("TAVILY_API_KEY") or "").strip():
        return True
    try:
        import ddgs  # noqa: F401

        return True
    except ImportError:
        pass
    try:
        import duckduckgo_search  # noqa: F401

        return True
    except ImportError:
        pass
    # Instant Answer 兜底始终可用（无额外包）
    return True


def active_backend_name() -> str:
    if (os.getenv("TAVILY_API_KEY") or "").strip():
        return "tavily"
    try:
        import ddgs  # noqa: F401

        return "ddgs"
    except ImportError:
        pass
    try:
        import duckduckgo_search  # noqa: F401

        return "ddgs(duckduckgo_search)"
    except ImportError:
        pass
    return "duckduckgo-instant"


registry.register(
    name="web_search",
    toolset="web",
    schema=WEB_SEARCH_SCHEMA,
    handler=lambda args, **kw: web_search_tool(
        query=args.get("query", ""),
        limit=args.get("limit", 5),
    ),
    check_fn=check_web_search_requirements,
    emoji="🔍",
)
