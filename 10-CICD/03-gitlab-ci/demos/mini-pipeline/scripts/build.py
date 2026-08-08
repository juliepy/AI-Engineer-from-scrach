"""Build job: write a versioned 'package' under dist/ (SHA-tagged, no latest)."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.calculator import __version__, version_string


def resolve_sha(explicit: str | None) -> str:
    if explicit:
        return explicit
    # Prefer real git SHA when available; fall back to content hash.
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass

    h = hashlib.sha1()
    for path in sorted((ROOT / "app").rglob("*.py")):
        h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", default=None, help="Commit SHA (default: git HEAD or content hash)")
    args = parser.parse_args()

    sha = resolve_sha(args.sha)
    label = version_string(sha)
    dist = Path("dist")
    dist.mkdir(exist_ok=True)

    # Clean previous packages so release tests see one clear artifact.
    for old in dist.glob("mini-app-*.txt"):
        old.unlink()

    out = dist / f"{label}.txt"
    out.write_text(
        "\n".join(
            [
                "name=mini-app",
                f"version={__version__}",
                f"commit={sha}",
                f"label={label}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    artifacts = Path("artifacts")
    artifacts.mkdir(exist_ok=True)
    copied = artifacts / out.name
    copied.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[build] wrote {out}")
    print(f"[build] copied {copied}")


if __name__ == "__main__":
    main()
