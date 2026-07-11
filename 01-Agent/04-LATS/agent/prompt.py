def build_expand_prompt(state: str, k: int, tool_names: list[str]) -> str:
    tools = ", ".join(tool_names)
    return "\n".join(
        [
            f"State:\n{state}",
            f"Propose {k} distinct next actions (one line each).",
            f"Use format: Action: <one of {tools}>[input]  or  Thought: <reasoning>",
            "Output only the action lines, no numbering.",
        ]
    )


def build_rollout_prompt(state: str, depth: int) -> str:
    return "\n".join(
        [
            "Rate how promising this partial plan is for completing the task.",
            "Reply with ONLY a float from 0.0 to 1.0.",
            f"State:\n{state}",
            f"Steps taken so far: {depth}",
        ]
    )


def build_llm_score_prompt(state: str, action: str) -> str:
    return "\n".join(
        [
            "Score this single next action for the given state.",
            "Reply with ONLY a float from 0.0 to 1.0.",
            f"State:\n{state}",
            f"Action:\n{action}",
        ]
    )
