from langchain_core.messages import AIMessage

from backend.agents.base import build_react_agent, invoke_react_agent
from backend.state import TravelState

FINAL_SYSTEM_PROMPT = """
You are the Final Response Agent in a multi-agent travel planning system.

You receive briefings from the flight, hotel, and itinerary specialist agents.
Your job is to synthesize one polished, user-facing travel plan.

Format the answer with these sections:
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Rules:
- Be clear and practical.
- Do not invent facts beyond the specialist briefings.
- Mention that live flight APIs may not provide ticket prices when pricing is unavailable.
- Write for real travel planning usefulness.
""".strip()

# No tools: this agent only synthesizes upstream specialist outputs.
_final_react_agent = build_react_agent(
    tools=[],
    system_prompt=FINAL_SYSTEM_PROMPT,
    name="final_react_agent",
)


def final_agent(state: TravelState):
    """Parent-graph node: run the final synthesis agent."""
    answer, calls = invoke_react_agent(
        _final_react_agent,
        (
            "Produce the final travel response for the user.\n\n"
            f"User request:\n{state['user_query']}\n\n"
            f"Flight agent briefing:\n{state.get('flight_results') or '(none)'}\n\n"
            f"Hotel agent briefing:\n{state.get('hotel_results') or '(none)'}\n\n"
            f"Itinerary agent draft:\n{state.get('itinerary') or '(none)'}"
        ),
    )

    return {
        "messages": [AIMessage(content=answer)],
        "llm_calls": state.get("llm_calls", 0) + calls,
    }
