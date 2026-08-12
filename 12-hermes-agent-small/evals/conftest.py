import os
import sys
from pathlib import Path

import pytest

# evals/ sits next to waku/, not inside it — make both importable when
# running `pytest evals` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# apply_settings() writes these via os.environ[k] = v (bypassing monkeypatch).
# Snapshot/restore every test so a dashboard unit test can't leave
# WAKU_MODEL=kimi-k3 on a deepseek provider for later live evals.
_WAKU_ENV = (
    "WAKU_PROVIDER",
    "WAKU_MODEL",
    "WAKU_SMALL_MODEL",
    "WAKU_EPISODIC_STORE",
    "WAKU_HOME",
)


@pytest.fixture(autouse=True)
def _restore_waku_env_after_test():
    snap = {k: os.environ.get(k) for k in _WAKU_ENV}
    yield
    for k, v in snap.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
