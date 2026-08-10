"""LangChain tool wrappers used by ReAct agents."""

from langchain_core.tools import tool

from backend.tools.flight_tool import search_flights as _search_flights
from backend.tools.tavily_tool import tavily_search as _tavily_search


@tool
def search_flights(query: str) -> str:
    """Search live flight status via AviationStack from a natural-language travel query.

    Prefer including origin/destination cities or airport codes when possible.
    Note: this returns live/status data, not ticket prices.
    """
    return _search_flights(query)


@tool
def search_web(query: str) -> str:
    """Search the web with Tavily for hotels, attractions, or travel tips."""
    return _tavily_search(query)
