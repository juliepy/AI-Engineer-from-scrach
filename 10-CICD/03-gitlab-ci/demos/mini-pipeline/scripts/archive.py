"""Archive stage: collect test reports + scan report + packages into one bundle.

Corresponds to textbook step: 报告归档 / artifacts retention.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DIST = ROOT / "dist"
ARCHIVE_ROOT = ARTIFACTS / "archive"


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = ARCHIVE_ROOT / stamp
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    copied: list[str] = []

    def copy_if_exists(src: Path) -> None:
        if src.is_file():
            dest = bundle / src.name
            shutil.copy2(src, dest)
            copied.append(src.name)

    # Standard textbook pipeline outputs (plus any gate reports if present)
    for name in (
        "checkout-meta.json",
        "scan-report.json",
        "report-standard.xml",
        "report-mr.xml",
        "report-gate1.xml",
        "report-daily.xml",
        "report-release.xml",
    ):
        copy_if_exists(ARTIFACTS / name)

    # Prefer a clean teaching bundle: if standard report exists, still OK to
    # include optional gate reports; MANIFEST lists exactly what was copied.

    # Packages from dist/
    if DIST.is_dir():
        for pkg in DIST.glob("mini-app-*.txt"):
            shutil.copy2(pkg, bundle / pkg.name)
            copied.append(pkg.name)

    if not copied:
        print("[archive] nothing to archive — did earlier stages run?")
        return 1

    manifest = {
        "stage": "archive",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
        "files": copied,
        "note": "In GitLab these would be job artifacts downloadable from the UI.",
    }
    (bundle / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # Convenience pointer to latest
    latest = ARCHIVE_ROOT / "LATEST.txt"
    latest.write_text(str(bundle) + "\n", encoding="utf-8")

    print(f"[archive] bundle={bundle}")
    for name in copied:
        print(f"  + {name}")
    print(f"[archive] wrote {bundle / 'MANIFEST.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
