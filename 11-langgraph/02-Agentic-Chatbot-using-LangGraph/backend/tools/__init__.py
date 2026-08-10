from backend.startup_log import startup_log

startup_log("[tools] importing llm ...")
from backend.llm import llm

startup_log("[tools] importing rag_tool ...")
from backend.rag import rag_tool

startup_log("[tools] importing calculator/search/stock/weather ...")
from backend.tools.calculator import calculator
from backend.tools.search import search_tool
from backend.tools.stock import get_stock_price, purchase_stock
from backend.tools.weather import get_current_weather

startup_log("[tools] binding tools to llm ...")

tools = [
    search_tool,
    calculator,
    get_stock_price,
    get_current_weather,
    rag_tool,
    purchase_stock,
]

llm_with_tools = llm.bind_tools(tools)
startup_log("[tools] ready")

__all__ = [
    "tools",
    "llm_with_tools",
    "search_tool",
    "calculator",
    "get_stock_price",
    "purchase_stock",
    "get_current_weather",
]
