from langchain_core.messages import AIMessage

from backend.agents.base import build_react_agent, invoke_react_agent
from backend.state import TravelState
from backend.tools.langchain_tools import search_web

HOTEL_SYSTEM_PROMPT = """
You are the Hotel Research Agent in a multi-agent travel planning system.

Responsibilities:
- Use the `search_web` tool to find hotels that match the destination, dates/duration, and budget cues.
- Prefer practical options (location, value, traveler fit) over generic lists.
- Summarize 3-5 hotel suggestions with brief reasons.
- Use flight context when available to stay consistent with the destination.
- Do not invent hotel details that are not supported by search results.
""".strip()

_hotel_react_agent = build_react_agent(
    tools=[search_web],
    system_prompt=HOTEL_SYSTEM_PROMPT,
    name="hotel_react_agent",
)


def hotel_agent(state: TravelState):
    """Parent-graph node: run the hotel ReAct agent and store its findings."""
    answer, calls = invoke_react_agent(
        _hotel_react_agent,
        (
            "Find suitable hotels for this trip.\n\n"
            f"User query:\n{state['user_query']}\n\n"
            f"Flight agent briefing:\n{state.get('flight_results') or '(none yet)'}\n\n"
            "Call `search_web` at least once, then return a concise hotel briefing."
        ),
    )

    return {
        "hotel_results": answer,
        "messages": [AIMessage(content=f"[hotel_agent]\n{answer}")],
        "llm_calls": state.get("llm_calls", 0) + calls,
    }
