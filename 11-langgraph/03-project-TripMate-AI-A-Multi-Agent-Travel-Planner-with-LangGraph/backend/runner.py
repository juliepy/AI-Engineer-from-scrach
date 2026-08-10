import uuid
from typing import Any, Iterator

from langchain_core.messages import HumanMessage

from backend.graph import travel_graph

AGENT_PIPELINE = [
    "flight_agent",
    "hotel_agent",
    "itinerary_agent",
    "final_agent",
]

AGENT_LABELS = {
    "flight_agent": "航班调研",
    "hotel_agent": "酒店调研",
    "itinerary_agent": "行程规划",
    "final_agent": "最终回复",
}


def _initial_state(user_input: str) -> dict[str, Any]:
    return {
        "messages": [HumanMessage(content=user_input)],
        "user_query": user_input,
        "flight_results": "",
        "hotel_results": "",
        "itinerary": "",
        "llm_calls": 0,
    }


def _result_from_state(thread_id: str, values: dict[str, Any]) -> dict[str, Any]:
    messages = values.get("messages") or []
    final_answer = messages[-1].content if messages else ""
    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": values.get("flight_results", ""),
        "hotel_results": values.get("hotel_results", ""),
        "itinerary": values.get("itinerary", ""),
        "llm_calls": values.get("llm_calls", 0),
    }


def run_travel_agent(user_input: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable": {"thread_id": thread_id}}
    result = travel_graph.invoke(_initial_state(user_input), config=config)
    return _result_from_state(thread_id, result)


def stream_travel_agent(
    user_input: str,
    thread_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield progress events while the multi-agent graph runs, then a final result."""
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable": {"thread_id": thread_id}}
    total = len(AGENT_PIPELINE)

    yield {
        "type": "start",
        "thread_id": thread_id,
        "nodes": [
            {"id": node, "label": AGENT_LABELS.get(node, node)}
            for node in AGENT_PIPELINE
        ],
        "total": total,
    }

    # stream_mode="updates" fires after a node finishes; announce the first
    # node as running up front so the UI can show live progress.
    first = AGENT_PIPELINE[0]
    yield {
        "type": "progress",
        "thread_id": thread_id,
        "node": first,
        "label": AGENT_LABELS[first],
        "status": "running",
        "step": 1,
        "total": total,
    }

    for update in travel_graph.stream(
        _initial_state(user_input),
        config=config,
        stream_mode="updates",
    ):
        for node_name in update:
            if node_name not in AGENT_PIPELINE:
                continue

            step = AGENT_PIPELINE.index(node_name) + 1
            yield {
                "type": "progress",
                "thread_id": thread_id,
                "node": node_name,
                "label": AGENT_LABELS.get(node_name, node_name),
                "status": "done",
                "step": step,
                "total": total,
            }

            if step < total:
                nxt = AGENT_PIPELINE[step]
                yield {
                    "type": "progress",
                    "thread_id": thread_id,
                    "node": nxt,
                    "label": AGENT_LABELS[nxt],
                    "status": "running",
                    "step": step + 1,
                    "total": total,
                }

    state = travel_graph.get_state(config)
    yield {
        "type": "result",
        **_result_from_state(thread_id, state.values),
    }
