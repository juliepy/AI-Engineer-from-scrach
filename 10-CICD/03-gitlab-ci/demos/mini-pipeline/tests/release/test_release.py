from pathlib import Path

import pytest

from app.calculator import version_string


@pytest.mark.release
def test_dist_artifact_exists():
    """Release gate: package must already be built (build job first)."""
    dist = Path("dist")
    assert dist.is_dir(), "dist/ missing — run build stage first"
    packages = list(dist.glob("mini-app-*.txt"))
    assert packages, "no mini-app-*.txt in dist/"


@pytest.mark.release
def test_version_string_not_latest():
    label = version_string("deadbeef")
    assert "latest" not in label.lower()
