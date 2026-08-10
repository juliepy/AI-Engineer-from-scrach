import os
from typing import Any

from langchain_core.tools import tool
from tavily import TavilyClient

from backend.logger import get_logger

logger = get_logger(__name__)


@tool
def get_current_weather(location: str) -> str:
    """
    Get the current real-time weather for a given city or location.

    Args:
        location: City or location name, for example:
                  "Dhaka", "London, UK", or "New York, US".

    Returns:
        A formatted current weather report.
    """
    logger.info("get_current_weather called | location=%s", location)
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        logger.warning("TAVILY_API_KEY is missing")
        return (
            "Weather search API key is missing. "
            "Set the TAVILY_API_KEY environment variable."
        )

    try:
        client = TavilyClient(api_key=api_key)
        query = f"current weather in {location} today temperature humidity wind"

        response: dict[str, Any] = client.search(
            query=query,
            max_results=5,
            search_depth="basic",
            include_answer=True,
            topic="general",
            time_range="day",
        )

        answer = response.get("answer")
        results = response.get("results") or []

        if answer:
            sources = []
            for item in results[:3]:
                title = item.get("title") or "Source"
                url = item.get("url") or ""
                if url:
                    sources.append(f"- {title}: {url}")

            source_block = (
                "\n\nSources:\n" + "\n".join(sources) if sources else ""
            )
            logger.info("get_current_weather success | location=%s", location)
            return (
                f"Current weather for {location} (via Tavily):\n"
                f"{answer}"
                f"{source_block}"
            )

        if not results:
            return f"Could not find current weather information for: {location}"

        snippets = []
        for item in results[:3]:
            title = item.get("title") or "Result"
            content = (item.get("content") or "").strip()
            url = item.get("url") or ""
            line = f"- {title}: {content}"
            if url:
                line += f" ({url})"
            snippets.append(line)

        logger.info("get_current_weather success | location=%s", location)
        return (
            f"Current weather for {location} (via Tavily):\n"
            + "\n".join(snippets)
        )

    except Exception as error:
        logger.exception(
            "get_current_weather failed | location=%s | error=%s",
            location,
            error,
        )
        return f"Could not fetch weather via Tavily: {error}"
