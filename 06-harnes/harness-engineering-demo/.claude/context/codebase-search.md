# Codebase-Search MCP Tools

The repo ships a FastMCP server at `tooling/mcp/codebase_search.py`, wired in via `.mcp.json` as `codebase-search`. It parses the project's Python source into an AST and exposes three structured-search tools. Use these instead of grep when you need to navigate by symbol.

---

## Tools

### `where_is(name)`

Find every definition of `name` — a function, method, class, or module-level constant.

Returns the file path, line number, kind, and fully-qualified name. For functions and methods it also returns the full signature.

**Use when:** you need to locate a function before reading it, or confirm a symbol is defined where you expect.

```
where_is("list_meetings")
→  app/backend/app/routes/routes_meetings.py:42  [function]  def list_meetings(...)
```

### `find_references(name)`

Find every place `name` is used — function calls, attribute access, and name loads — across all Python source in the project.

Deduplicated to one result per line (call > attribute > name), so a `foo(...)` call site appears once as `[call]`, not as both `[call]` and `[name]`.

**Use when:** you want to verify a dependency is actually applied in new code (e.g., `find_references("get_current_user")` to confirm a new route uses JWT auth), or to see all callers before refactoring a function.

```
find_references("get_db")
→  app/backend/app/routes/routes_meetings.py:51  [call]  get_db(...)
→  app/backend/app/routes/routes_contacts.py:38  [call]  get_db(...)
```

### `outline(module)`

Show the structured public API of one module — classes, methods, and functions with full signatures, in source order.

`module` accepts a file path (`app/backend/app/services/export_service.py`) or a dotted module name (`export_service`, or `services.export_service`).

**Use when:** you need to understand what a service exposes before adding a method, or verify the shape of a module before reading its full source.

```
outline("export_service")
→  outline of app/backend/app/services/export_service.py:
     12: [class] class ExportService
         22: [method] def export_meetings_csv(self, meetings, ...) -> bytes
         48: [method] def _escape_cell(self, value: str) -> str
```

---

## Scope

The server walks the project from `CLAUDE_PROJECT_DIR` (or cwd if unset), skipping:

`.git`, `.venv`, `venv`, `env`, `node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build`, `dist`, `.claude`, `.tox`, `site-packages`

It covers **Python source only** — TypeScript/frontend files are not indexed.

---

## MCP server wiring

`.mcp.json` at the repo root tells Claude Code to start the server with:

```
uv run --directory tooling python mcp/codebase_search.py
```

The `tooling/pyproject.toml` declares the `mcp` dependency so it runs in an isolated environment, separate from the app's `uv.lock`.
