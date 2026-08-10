from langchain_core.messages import AIMessage

from backend.agents.base import build_react_agent, invoke_react_agent
from backend.state import TravelState
from backend.tools.langchain_tools import search_flights

FLIGHT_SYSTEM_PROMPT = """
You are the Flight Research Agent in a multi-agent travel planning system.

Responsibilities:
- Understand the user's origin, destination, and trip intent.
- Use the `search_flights` tool to gather live flight/status information.
- Summarize useful flight options clearly for downstream agents.
- If the tool returns no prices, explicitly note that AviationStack is live/status data, not fare quotes.
- Do not invent flights that the tool did not return.
""".strip()

_flight_react_agent = build_react_agent(
    tools=[search_flights],
    system_prompt=FLIGHT_SYSTEM_PROMPT,
    name="flight_react_agent",
)


def flight_agent(state: TravelState):
    """Parent-graph node: run the flight ReAct agent and store its findings."""
    answer, calls = invoke_react_agent(
        _flight_react_agent,
        (
            "Research flights for this travel request.\n\n"
            f"User query:\n{state['user_query']}\n\n"
            "Call `search_flights` at least once, then return a concise flight briefing."
        ),
    )

    return {
        "flight_results": answer,
        "messages": [AIMessage(content=f"[flight_agent]\n{answer}")],
        "llm_calls": state.get("llm_calls", 0) + calls,
    }
