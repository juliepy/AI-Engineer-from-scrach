"""*_test.py 命名也会被收集；演示 fixture。"""

import pytest


@pytest.fixture
def client():
    return {"ok": True, "name": "demo"}


def test_api(client):
    assert client["ok"] is True
    assert client["name"] == "demo"
