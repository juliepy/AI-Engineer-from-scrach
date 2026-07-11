from typing import Callable, Dict, List, Tuple

from agent.prompt import build_prompt, parse_action
from agent.types import Tool


def react_loop(
    question: str,
    tools: Dict[str, Tool],
    llm: Callable[[str], str],
    max_steps: int = 6,
    verbose: bool = False,
) -> str:
    """单步 ReAct 执行器：完成一个子任务后返回 Final Answer。"""
    history: List[Tuple[str, str, str]] = []
    for step in range(1, max_steps + 1):
        prompt = build_prompt(question, history, tools)
        print("\n\n----------------------------------------------------------------")
        print(f"React loop prompt: {prompt}")
        print("----------------------------------------------------------------")
        out = llm(prompt)
        print("\n\n----------------------------------------------------------------")
        print(f"React loop out: {out}")
        print("----------------------------------------------------------------")

        if verbose:
            print(f"\n--- ReAct Step {step} ---")
            print(out)

        if "Final Answer:" in out:
            answer = out.split("Final Answer:", 1)[1].strip()
            if verbose:
                print(f">>> Final Answer: {answer}")
            return answer

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

    return "Failed: max steps exceeded."
