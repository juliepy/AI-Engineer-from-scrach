import json
from typing import Callable, Dict, List, Tuple

from agent.prompt import build_prompt, parse_action
from agent.types import Tool

# history 每条为 (thought, action, action_input, observation)
HistoryItem = Tuple[str, str, str, str]


def _print_tool_execution(action: str, action_input: str, observation: str) -> None:
    print("\n=======>>> Tool execution ======\n")
    print(json.dumps(
        {"action": action, "input": action_input, "observation": observation},
        indent=2,
        ensure_ascii=False,
    ))


def react_loop(
    question: str,
    tools: Dict[str, Tool],
    llm: Callable[[str], str],
    max_steps: int = 6,
) -> str:
    history: List[HistoryItem] = []
    for step in range(1, max_steps + 1):
        print(f"\n--- Step {step} ---")
        prompt = build_prompt(question, history, tools)
        out = llm(prompt)

        action, action_input = parse_action(out)

        # 有合法工具可执行时，先执行工具；忽略同条回复里的 Final Answer
        if action and action in tools:
            thought = ""
            for line in out.splitlines():
                if line.startswith("Thought:"):
                    thought = line.split("Thought:", 1)[1].strip()
                    break
            obs = tools[action].run(action_input or "")
            _print_tool_execution(action, action_input or "", obs)
            history.append((thought, action, action_input or "", obs))
            continue

        if "Final Answer:" in out:
            answer = out.split("Final Answer:", 1)[1].strip()
            print(f"\n=====> Model>\t {answer}\n")
            return answer

        obs = f"ERROR: invalid Action. Must be one of {list(tools.keys())}."
        _print_tool_execution(action or "", action_input or "", obs)
        history.append(("", action or "", action_input or "", obs))

    return "Failed: max steps exceeded."
