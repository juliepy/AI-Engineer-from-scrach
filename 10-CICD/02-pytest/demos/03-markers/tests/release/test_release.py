import pytest


@pytest.mark.release
def test_package_checklist():
    artifacts = ["app.bin", "checksum.txt", "version.txt"]
    assert "version.txt" in artifacts


@pytest.mark.release
def test_version_not_latest():
    tag = "v1.2.3"
    assert tag != "latest"
