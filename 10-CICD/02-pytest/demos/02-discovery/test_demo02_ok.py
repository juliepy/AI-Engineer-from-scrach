"""会被收集：文件名 test_*.py + 函数 test_* + 类 Test*。"""


def test_login_ok():
    assert True


def test_login_token():
    token = "abc"
    assert token.startswith("a")


class TestUser:
    def test_create(self):
        assert 1 == 1

    def test_delete(self):
        assert "user" in "create_user"
