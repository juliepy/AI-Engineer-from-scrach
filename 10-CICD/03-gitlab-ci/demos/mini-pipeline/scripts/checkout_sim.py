"""Simulate: MR trigger + Runner checkout (git pull).

In real GitLab this happens before your jobs; here we make it visible
so the textbook pipeline steps are complete.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
META = OUT / "checkout-meta.json"


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    sha = git("rev-parse", "HEAD") or "local-no-git"
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "local"
    tracked = git("ls-files")
    files = [line for line in tracked.splitlines() if line] if tracked else [
        str(p.relative_to(ROOT)).replace("\\", "/")
        for p in ROOT.rglob("*")
        if p.is_file() and ".venv" not in p.parts and p.name != ".gitignore"
    ][:40]

    meta = {
        "event": "merge_request_event (simulated)",
        "step": "checkout",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": branch,
        "commit": sha,
        "workdir": str(ROOT),
        "files_sample": files[:20],
        "file_count": len(files),
        "note": "Real GitLab Runner clones the repo before jobs; this job only demonstrates the step.",
    }
    META.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("[trigger] simulated MR / pipeline trigger")
    print(f"[checkout] branch={branch} commit={sha[:12]}")
    print(f"[checkout] workdir={ROOT}")
    print(f"[checkout] tracked files≈{len(files)}")
    print(f"[checkout] wrote {META}")


if __name__ == "__main__":
    main()
