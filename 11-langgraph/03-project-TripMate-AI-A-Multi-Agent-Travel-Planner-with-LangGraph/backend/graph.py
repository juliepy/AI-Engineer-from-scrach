from langgraph.graph import END, START, StateGraph

from backend.agents import final_agent, flight_agent, hotel_agent, itinerary_agent
from backend.database import create_checkpointer
from backend.state import TravelState


def build_travel_graph():
    """Sequential multi-agent handoff: each node is a specialist ReAct agent."""
    graph = StateGraph(TravelState)

    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("final_agent", final_agent)

    # Specialist agents collaborate by writing into shared TravelState, then handing off.
    graph.add_edge(START, "flight_agent")
    graph.add_edge("flight_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", "final_agent")
    graph.add_edge("final_agent", END)

    return graph.compile(checkpointer=create_checkpointer())


travel_graph = build_travel_graph()
