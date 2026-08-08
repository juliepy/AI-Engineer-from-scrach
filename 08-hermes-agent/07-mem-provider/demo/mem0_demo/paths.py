"""01 · Paths & constants (isolated HERMES_HOME, never ~/.hermes)."""

from __future__ import annotations

from pathlib import Path

# demo/  (parent of this package)
DEMO_ROOT = Path(__file__).resolve().parent.parent
# 07-mem-provider/
MODULE_ROOT = DEMO_ROOT.parent

EXPORTS = DEMO_ROOT / "exports" / "mem_provider"
HERMES_HOME_DEMO = DEMO_ROOT / ".hermes_demo"

SESSION_ID = "mem0-demo-sess"
USER_ID = "mem0-demo-user"
