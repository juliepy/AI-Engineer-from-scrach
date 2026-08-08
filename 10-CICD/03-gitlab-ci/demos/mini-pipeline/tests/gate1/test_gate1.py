import pytest

from app.calculator import add, version_string


@pytest.mark.gate1
def test_add_critical_path():
    """Post-merge critical: slightly broader than smoke."""
    assert add(10, 5) == 15
    assert add(0, 0) == 0


@pytest.mark.gate1
def test_version_label_shape():
    label = version_string("abcdef1234567890")
    assert label.startswith("mini-app-")
    assert "+abcdef12" in label
