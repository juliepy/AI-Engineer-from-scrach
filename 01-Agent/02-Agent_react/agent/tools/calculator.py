import ast
import operator


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval_ast(node.left), _eval_ast(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_ast(node.operand))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")


def run(expr: str) -> str:
    """安全计算器：只支持 + - * / // % ** 和括号。"""
    expr = expr.strip()
    if not expr:
        return "ERROR: empty expression"
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_eval_ast(tree.body))
    except Exception as exc:
        return f"ERROR: {exc}"
