"""Codebase-search MCP server for Helpline — AST-based structured search.

The article: "the most sophisticated teams built MCP servers exposing
structured search as a tool Claude can call directly."

*Structured* is the operative word. This server parses every module into a
Python AST and answers questions about code **structure** — definitions,
references, and module shape. It never substring-matches: grep already does
that, and the article is explicit that moving past text-pattern matching is the
whole point. `where_is` returns only real `def`/`class`/constant nodes;
`find_references` returns only real call/attribute/name nodes — no false hits
from comments, strings, or unrelated identifiers.

Runs over stdio; wired into the repo via `.mcp.json`, and bundled in the
`helpline-ai-layer` plugin so it travels to any repo — it discovers Python
source by walking the project, so it is not tied to Helpline's layout.

Tools:
  - where_is(name)        : every definition of `name` — function, method,
                            class, or module constant — with kind + qualname.
  - find_references(name) : every use of `name` — calls, attribute access,
                            name loads — across the repo's Python source.
  - outline(module)       : the structured public API of a module — classes,
                            methods, and functions with full signatures.

Run directly:  uv run --extra dev python tooling/mcp/codebase_search.py
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Resolve against the project Claude Code is operating in — so the same server
# works repo-local (via .mcp.json) and bundled in the plugin (any repo).
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())

# Dependencies, caches, build output, and AI-Layer config are never "the
# codebase" — skip them so the index is repo source only, in any repo.
EXCLUDE_DIRS = frozenset({
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist",
    ".claude", ".tox", "site-packages",
})

mcp = FastMCP("helpline-codebase-search")


@dataclass(frozen=True)
class Definition:
    path: str
    line: int
    kind: str  # "function" | "method" | "class" | "constant"
    qualname: str
    signature: str


@dataclass(frozen=True)
class Reference:
    path: str
    line: int
    kind: str  # "call" | "attribute" | "name"
    text: str


# --- file discovery & parsing -------------------------------------------------


def _python_files() -> list[Path]:
    """Every Python source file in the project, minus dependency/cache/build
    directories — layout-agnostic, so this works in any repo. Uses a pruning
    walk so it never descends into node_modules / .venv."""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(Path(dirpath) / filename)
    return sorted(files)


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return None


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _module_name(path: Path) -> str:
    return _rel(path).removesuffix(".py").replace("/", ".")


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args}){returns}"


# --- AST visitors -------------------------------------------------------------


class _DefCollector(ast.NodeVisitor):
    """Collects every definition in one module, in source order, tracking the
    enclosing class/function stack so qualified names are accurate."""

    def __init__(self, module: str, relpath: str) -> None:
        self.module = module
        self.relpath = relpath
        self.stack: list[tuple[str, str]] = []  # (name, "class" | "func")
        self.defs: list[Definition] = []

    def _qual(self, name: str) -> str:
        return ".".join([self.module, *(n for n, _ in self.stack), name])

    def _enclosing_is_class(self) -> bool:
        return bool(self.stack) and self.stack[-1][1] == "class"

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.defs.append(
            Definition(
                self.relpath, node.lineno, "class",
                self._qual(node.name), f"class {node.name}",
            )
        )
        self.stack.append((node.name, "class"))
        self.generic_visit(node)
        self.stack.pop()

    def _record_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        kind = "method" if self._enclosing_is_class() else "function"
        self.defs.append(
            Definition(
                self.relpath, node.lineno, kind,
                self._qual(node.name), _signature(node),
            )
        )
        self.stack.append((node.name, "func"))
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_func(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self.stack:  # module-level constants only
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defs.append(
                        Definition(
                            self.relpath, node.lineno, "constant",
                            self._qual(target.id), target.id,
                        )
                    )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not self.stack and isinstance(node.target, ast.Name):
            self.defs.append(
                Definition(
                    self.relpath, node.lineno, "constant",
                    self._qual(node.target.id), node.target.id,
                )
            )
        self.generic_visit(node)


class _RefCollector(ast.NodeVisitor):
    """Collects every reference to one name in a module."""

    def __init__(self, relpath: str, name: str) -> None:
        self.relpath = relpath
        self.name = name
        self.refs: list[Reference] = []

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        called = (
            func.id if isinstance(func, ast.Name)
            else func.attr if isinstance(func, ast.Attribute)
            else None
        )
        if called == self.name:
            self.refs.append(
                Reference(self.relpath, node.lineno, "call", f"{self.name}(...)")
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == self.name:
            self.refs.append(
                Reference(self.relpath, node.lineno, "attribute", f".{self.name}")
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == self.name and isinstance(node.ctx, ast.Load):
            self.refs.append(
                Reference(self.relpath, node.lineno, "name", self.name)
            )
        self.generic_visit(node)


# --- index helpers ------------------------------------------------------------


def _all_definitions() -> list[Definition]:
    defs: list[Definition] = []
    for path in _python_files():
        tree = _parse(path)
        if tree is None:
            continue
        collector = _DefCollector(_module_name(path), _rel(path))
        collector.visit(tree)
        defs.extend(collector.defs)
    return defs


def _references(name: str) -> list[Reference]:
    """All references to `name`, deduplicated to one per line (a call site is
    also a name load — keep the most specific kind)."""
    priority = {"call": 0, "attribute": 1, "name": 2}
    found: dict[tuple[str, int], Reference] = {}
    for path in _python_files():
        tree = _parse(path)
        if tree is None:
            continue
        collector = _RefCollector(_rel(path), name)
        collector.visit(tree)
        for ref in collector.refs:
            key = (ref.path, ref.line)
            existing = found.get(key)
            if existing is None or priority[ref.kind] < priority[existing.kind]:
                found[key] = ref
    return sorted(found.values(), key=lambda r: (r.path, r.line))


def _resolve_module(query: str) -> Path | None:
    norm = query.strip().removesuffix(".py").replace("\\", "/")
    dotted = norm.replace("/", ".")
    for path in _python_files():
        module = _module_name(path)
        rel = _rel(path).removesuffix(".py")
        if module == dotted or rel == norm:
            return path
        if module.endswith("." + dotted) or rel.endswith("/" + norm):
            return path
    return None


# --- MCP tools ----------------------------------------------------------------


@mcp.tool()
def where_is(name: str) -> str:
    """Find every definition of `name` — a function, method, class, or
    module-level constant — by parsing the AST of the project's Python source.

    Unlike a text search, this matches only real definitions: no hits from
    comments, docstrings, string literals, or identically-spelled locals.
    """
    hits = [d for d in _all_definitions() if d.qualname.rsplit(".", 1)[-1] == name]
    if not hits:
        return f"no definition of {name!r} found in the project's Python source"
    lines = [f"{len(hits)} definition(s) of {name!r}:"]
    for d in sorted(hits, key=lambda d: (d.path, d.line)):
        lines.append(f"  {d.path}:{d.line}  [{d.kind}] {d.qualname}")
        if d.kind in ("function", "method"):
            lines.append(f"      {d.signature}")
    return "\n".join(lines)


@mcp.tool()
def find_references(name: str) -> str:
    """Find every place `name` is used — function calls, attribute access, and
    name loads — across the project's Python source, parsed from the AST.

    This is the article's "find all references" done structurally: it returns
    only genuine references, not every textual mention.
    """
    refs = _references(name)
    if not refs:
        return f"no references to {name!r} found in the project's Python source"
    lines = [f"{len(refs)} reference(s) to {name!r}:"]
    for r in refs:
        lines.append(f"  {r.path}:{r.line}  [{r.kind}] {r.text}")
    return "\n".join(lines)


@mcp.tool()
def outline(module: str) -> str:
    """Show the structured API of one module — its classes, methods, and
    functions with full signatures, in source order.

    `module` accepts a path (`services/billing/subscriptions.py`) or a dotted
    name (`services.billing.subscriptions`, or just `subscriptions`).
    """
    target = _resolve_module(module)
    if target is None:
        return f"no module matching {module!r} in the project's Python source"
    tree = _parse(target)
    if tree is None:
        return f"could not parse {_rel(target)}"
    collector = _DefCollector(_module_name(target), _rel(target))
    collector.visit(tree)
    if not collector.defs:
        return f"{_rel(target)} has no top-level definitions"
    lines = [f"outline of {_rel(target)}:"]
    for d in collector.defs:
        indent = "    " if d.kind == "method" else "  "
        lines.append(f"{indent}{d.line}: [{d.kind}] {d.signature}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
