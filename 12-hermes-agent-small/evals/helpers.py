"""Shared eval plumbing: a scripted fake LLM client for offline tests, and a
real-Waku factory for live ones."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace


def has_key() -> bool:
    """True when the ACTIVE provider (WAKU_PROVIDER) has its key set, so live
    evals run on whatever the user actually configured (anthropic, openrouter,
    gemini, ...), not only on ANTHROPIC_API_KEY.

    Computed at call time — earlier tests may mutate os.environ via
    dashboard.apply_settings, so an import-time snapshot would go stale.
    """
    from waku.config import load_settings
    from waku.loop.models import PROVIDERS

    settings = load_settings()
    provider = PROVIDERS.get(settings.provider)
    return bool(
        (settings.api_key or "").strip()
        or (provider and (os.getenv(provider.key_env) or "").strip())
    )


# Back-compat alias for collection-time skipif. Live tests also call has_key()
# at runtime because apply_settings can pollute os.environ mid-suite.
HAS_KEY = has_key()


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(name: str, args: dict, call_id: str = "tu_1"):
    return SimpleNamespace(type="tool_use", id=call_id, name=name, input=args)


def response(blocks, stop_reason="end_turn"):
    return SimpleNamespace(
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=0, output_tokens=0),
        content=blocks,
    )


class ScriptedClient:
    """Plays back a fixed list of responses — the 'model' for offline tests."""

    def __init__(self, script: list):
        self._script = list(script)
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        return self._script.pop(0)


def make_waku(home: Path, client=None, **settings_overrides):
    """Build a Waku with an isolated home dir; optionally swap in a fake client."""
    from waku.app import Waku
    from waku.config import Settings

    # evals must NEVER touch the real Apple Calendar, whatever .env says
    settings_overrides.setdefault("apple_calendar", False)
    settings = Settings(home=home, **settings_overrides)
    if client is not None and not settings.api_key:
        settings.api_key = "offline"  # never read the real key for scripted runs
    return Waku(settings=settings, client=client)
