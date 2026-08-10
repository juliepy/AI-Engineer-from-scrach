import sqlite3
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from backend.logger import get_logger
from backend.tools import llm_with_tools, tools

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHATBOT_DB_PATH = DATA_DIR / "chatbot.db"

logger = get_logger(__name__)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    """LLM node that can answer directly or call an appropriate tool."""
    message_count = len(state.get("messages", []))
    logger.info("chat_node invoked | history_messages=%s", message_count)

    system_message = SystemMessage(
        content=(
            "You are a helpful Agentic Chatbot with access to several tools.\n\n"
            "Tool usage instructions:\n"
            "- Use `rag_tool` for questions about the uploaded PDF or document. "
            "Always retrieve relevant document content before answering PDF-related questions.\n"
            "- Use `search_tool` for current events, recent information, or information "
            "that requires an internet search.\n"
            "- Use `calculator` for mathematical calculations. Do not calculate complex "
            "expressions manually when the calculator is available.\n"
            "- Use `get_stock_price` when the user asks for the current price of a stock.\n"
            "- Use `purchase_stock` when the user wants to purchase a stock.\n"
            "- Use `get_current_weather` when the user asks about current weather for a location.\n\n"
            "Answer general questions directly when no tool is required. "
            "Do not invent information from the uploaded document. "
            "If the user asks about a PDF but no document is available, ask them to upload a PDF. "
            "After receiving a tool result, provide a clear and helpful final answer."
        )
    )

    messages = [system_message, *state["messages"]]

    try:
        response = llm_with_tools.invoke(messages)
    except Exception:
        logger.exception("chat_node LLM invoke failed")
        raise

    tool_calls = getattr(response, "tool_calls", None) or []
    if tool_calls:
        tool_names = [call.get("name", "unknown") for call in tool_calls]
        logger.info("chat_node requested tools | tools=%s", tool_names)
    else:
        logger.info("chat_node produced direct answer")

    return {"messages": [response]}


tool_node = ToolNode(tools)

conn = sqlite3.connect(database=str(CHATBOT_DB_PATH), check_same_thread=False)
checkpoint = SqliteSaver(conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpoint)
