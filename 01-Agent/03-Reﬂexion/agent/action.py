from typing import Callable, Dict, List, Tuple

from agent.prompt import build_action_prompt, parse_action
from agent.types import Tool


def run_action(
    task: str,
    reflections: List[str],
    tools: Dict[str, Tool],
    llm: Callable[[str], str],
    max_steps: int = 6,
    verbose: bool = False,
) -> str:
    """Action：基于任务与 reflections，用 ReAct 生成输出（可含工具）。"""
    history: List[Tuple[str, str, str]] = []
    for step in range(1, max_steps + 1):
        prompt = build_action_prompt(task, reflections, history, tools)
        if verbose:
            print(f"\n--- Action Step {step} ---")
            print(prompt[:800] + ("..." if len(prompt) > 800 else ""))

        out = llm(prompt)
        if verbose:
            print(out)

        if "Final Answer:" in out:
            return out.split("Final Answer:", 1)[1].strip()

        thought = ""
        for line in out.splitlines():
            if line.startswith("Thought:"):
                thought = line.split("Thought:", 1)[1].strip()

        action, action_input = parse_action(out)
        if not action or action not in tools:
            obs = f"ERROR: invalid Action. Must be one of {list(tools.keys())}."
        else:
            obs = tools[action].run(action_input or "")
            if verbose:
                print(f"Observation: {obs}")

        history.append((thought, f"{action}[{action_input}]", obs))

    return "Failed: max action steps exceeded."
