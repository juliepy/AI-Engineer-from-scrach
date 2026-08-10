from langchain_core.messages import AIMessage

from backend.agents.base import build_react_agent, invoke_react_agent
from backend.state import TravelState
from backend.tools.langchain_tools import search_web

ITINERARY_SYSTEM_PROMPT = """
You are the Itinerary Planning Agent in a multi-agent travel planning system.

Responsibilities:
- Build a practical day-by-day itinerary from the user request plus flight/hotel briefings.
- Use the `search_web` tool when you need attractions, transit tips, or neighborhood ideas.
- Keep the plan budget-aware, geographically coherent, and realistic for the trip length.
- Output a structured draft itinerary for the final response agent to polish.
""".strip()

_itinerary_react_agent = build_react_agent(
    tools=[search_web],
    system_prompt=ITINERARY_SYSTEM_PROMPT,
    name="itinerary_react_agent",
)


def itinerary_agent(state: TravelState):
    """Parent-graph node: run the itinerary ReAct agent and store its draft plan."""
    answer, calls = invoke_react_agent(
        _itinerary_react_agent,
        (
            "Create a complete draft itinerary.\n\n"
            f"User query:\n{state['user_query']}\n\n"
            f"Flight agent briefing:\n{state.get('flight_results') or '(none)'}\n\n"
            f"Hotel agent briefing:\n{state.get('hotel_results') or '(none)'}\n\n"
            "You may call `search_web` for local attractions or tips, then return the draft itinerary."
        ),
    )

    return {
        "itinerary": answer,
        "messages": [AIMessage(content=f"[itinerary_agent]\n{answer}")],
        "llm_calls": state.get("llm_calls", 0) + calls,
    }
