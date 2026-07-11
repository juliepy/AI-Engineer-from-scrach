"""Tool: basic_calculator — 支持加减乘除的简单计算器。"""

SUPPORTED_OPS = ("add", "subtract", "multiply", "divide")


def basic_calculator(operation: str, a: float, b: float) -> str:
    """执行四则运算，返回带算式的结果字符串。"""
    op = (operation or "").strip().lower()
    if op not in SUPPORTED_OPS:
        return f"ERROR: unsupported operation '{operation}'. Supported: {SUPPORTED_OPS}"

    if op == "add":
        result = a + b
        expr = f"{a} + {b} = {result}"
    elif op == "subtract":
        result = a - b
        expr = f"{a} - {b} = {result}"
    elif op == "multiply":
        result = a * b
        expr = f"{a} × {b} = {result}"
    else:  # divide
        if b == 0:
            return "ERROR: division by zero"
        result = a / b
        expr = f"{a} ÷ {b} = {result}"

    return expr


# ── JSON Schema（供 OpenAI tools 参数使用）─────────────────────────────────────

SCHEMA = {
    "type": "function",
    "function": {
        "name": "basic_calculator",
        "description": (
            "执行两个数的基本四则运算（加减乘除）。"
            "operation 可选值：add（加）、subtract（减）、multiply（乘）、divide（除）。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "运算类型：add/subtract/multiply/divide。",
                },
                "a": {
                    "type": "number",
                    "description": "第一个操作数。",
                },
                "b": {
                    "type": "number",
                    "description": "第二个操作数。",
                },
            },
            "required": ["operation", "a", "b"],
        },
    },
}
