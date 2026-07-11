from typing import Callable, Dict

from agent.action import run_action
from agent.evaluator import evaluate
from agent.reflector import reflect, trim_reflections
from agent.types import Tool


def reflect_until_success(
    task: str,
    llm: Callable[[str], str],
    tools: Dict[str, Tool],
    max_trials: int = 3, # 最大尝试次数
    max_action_steps: int = 6,  # 最大动作步骤
    max_reflections: int = 5, # 最大反射次数
    verbose: bool = False, # 是否打印详细信息
) -> str:
    """
    Reflection 主循环：Action → Evaluation → Reflection → Retry。

    reflections = []
    repeat until success or max_trials:
        Action: 基于 task + reflections 生成输出
        Evaluation: score, feedback = Evaluator(output)
        if success: return output
        Reflection: reflections.append(Reflector(feedback))
    """
    reflections: list[str] = []
    last_output = ""

    for trial in range(1, max_trials + 1):
        if verbose:
            print(f"\n========== Trial {trial}/{max_trials} ==========")
            if reflections:
                print("Strategy memory:")
                for i, r in enumerate(reflections, 1):
                    print(f"  {i}. {r}")

        last_output = run_action(
            task,
            reflections,
            tools,
            llm,
            max_steps=max_action_steps,
            verbose=verbose,
        )

        if verbose:
            print(f"\n--- Evaluation ---")
            print(f"Output: {last_output}")

        result = evaluate(task, last_output, llm)
        if verbose:
            print(
                f"Success={result.success} Score={result.score}\n"
                f"Feedback: {result.feedback}"
            )

        if result.success:
            if verbose:
                print(f"\n>>> Success on trial {trial}")
            return last_output

        reflection = reflect(
            task,
            last_output,
            result.feedback,
            result.score,
            reflections,
            llm,
        )
        reflections = trim_reflections(reflections + [reflection], max_reflections)

        if verbose:
            print(f"\n--- Reflection appended ---\n{reflection}")

    return last_output or "Failed: max trials exceeded."
