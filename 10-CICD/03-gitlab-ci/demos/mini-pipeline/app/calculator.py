"""Tiny library so the pipeline has something real to lint / test / package."""

__version__ = "0.1.0"


def add(a: int, b: int) -> int:
    return a + b


def version_string(commit_sha: str = "local") -> str:
    """Build a release-style version label (SHA in real CI)."""
    short = (commit_sha or "local")[:8]
    return f"mini-app-{__version__}+{short}"
