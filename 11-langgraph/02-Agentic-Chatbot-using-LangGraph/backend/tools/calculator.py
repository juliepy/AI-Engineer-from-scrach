import math

from langchain_core.tools import tool

from backend.logger import get_logger

logger = get_logger(__name__)


@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10 * 5
    """
    logger.info("calculator called | expression=%s", expression)

    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        logger.info("calculator success | result=%s", result)
        return str(result)

    except Exception as e:
        logger.warning("calculator failed | expression=%s | error=%s", expression, e)
        return f"Calculation error: {str(e)}"
