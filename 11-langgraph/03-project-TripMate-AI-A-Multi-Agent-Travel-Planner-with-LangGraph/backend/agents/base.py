"""Helpers for building and invoking specialist ReAct agents."""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from backend.llm import llm


def build_react_agent(tools: list, system_prompt: str, name: str):
    """Create a tool-calling ReAct agent graph."""
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        name=name,
    )


def invoke_react_agent(agent, user_message: str) -> tuple[str, int]:
    """Run a specialist agent and return (final_text, llm_call_count)."""
    result = agent.invoke(
        {
            "messages": [HumanMessage(content=user_message)],
        }
    )
    messages = result.get("messages") or []
    answer = ""
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            answer = message.content
            break

    llm_calls = sum(1 for message in messages if isinstance(message, AIMessage))
    return answer, llm_calls
