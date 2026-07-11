from typing import Any, Callable, Dict

from agent.react_loop import react_loop
from agent.types import Tool


def execute_step(
    step: str,
    state: Dict[str, Any],
    tools: Dict[str, Tool],
    llm: Callable[[str], str],
    verbose: bool = False,
) -> str:
    """以 ReAct 作为单步执行器，结合已有 state 完成当前步骤。"""
    context = "\n".join(f"- {k}: {v}" for k, v in state.items()) or "(none)"
    question = (
        f"Complete this step only:\n{step}\n\n"
        f"Prior step results:\n{context}\n\n"
        "Use tools if needed, then give Final Answer succinctly."
    )
    return react_loop(question, tools, llm, max_steps=4, verbose=verbose)
