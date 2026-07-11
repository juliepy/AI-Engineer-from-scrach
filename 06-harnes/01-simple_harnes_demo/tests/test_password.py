import unittest

from app.password import check_strength, explain_strength, hash_password, verify_password


def _log(msg: str) -> None:
    print(f"[TEST] {msg}")


class PasswordStrengthTests(unittest.TestCase):
    def test_empty_password_is_weak(self) -> None:
        password = ""
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "weak")

    def test_short_password_is_weak(self) -> None:
        password = "Ab1"
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "weak")

    def test_single_kind_password_is_weak(self) -> None:
        password = "abcdef"
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "weak")

    def test_mixed_but_short_password_is_medium(self) -> None:
        password = "abc123"
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "medium")

    def test_strong_password(self) -> None:
        password = "Abc12345"
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "strong")

    def test_special_chars_only_is_weak(self) -> None:
        password = "!@#$%"
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "weak")

    def test_strong_with_special_chars(self) -> None:
        password = "Abc@3456"
        result = check_strength(password)
        _log(f"check_strength({password!r}) -> {result!r}")
        self.assertEqual(result, "strong")


class ExplainStrengthTests(unittest.TestCase):
    def test_empty_password(self) -> None:
        password = ""
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "weak")
        self.assertEqual(result["suggestions"], ["密码不能为空"])

    def test_too_short_with_missing_types(self) -> None:
        password = "a"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "weak")
        self.assertEqual(
            result["suggestions"],
            ["密码长度至少 6 位（当前 1 位）", "需要包含大写字母", "需要包含数字", "需要包含特殊字符"],
        )

    def test_too_short_all_types_present(self) -> None:
        password = "aA1"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "weak")
        self.assertEqual(result["suggestions"], ["密码长度至少 6 位（当前 3 位）", "需要包含特殊字符"])

    def test_weak_only_lowercase(self) -> None:
        password = "abcdef"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "weak")
        self.assertEqual(result["suggestions"], ["需要包含大写字母", "需要包含数字", "需要包含特殊字符"])

    def test_weak_only_digits(self) -> None:
        password = "123456"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "weak")
        self.assertEqual(result["suggestions"], ["需要包含小写字母", "需要包含大写字母", "需要包含特殊字符"])

    def test_medium_missing_uppercase(self) -> None:
        password = "abc123"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "medium")
        self.assertEqual(
            result["suggestions"],
            ["需要包含大写字母", "需要包含特殊字符", "建议将密码长度增加至 8 位以上"],
        )

    def test_medium_all_types_short(self) -> None:
        password = "Abc123"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "medium")
        self.assertEqual(result["suggestions"], ["需要包含特殊字符", "建议将密码长度增加至 8 位以上"])

    def test_medium_length_7(self) -> None:
        password = "Abcdef1"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "medium")
        self.assertEqual(result["suggestions"], ["需要包含特殊字符", "建议将密码长度增加至 8 位以上"])

    def test_medium_long_but_missing_digit(self) -> None:
        password = "Abcdefgh"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "medium")
        self.assertEqual(result["suggestions"], ["需要包含数字", "需要包含特殊字符"])

    def test_strong_password(self) -> None:
        password = "Abc12345"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "strong")
        self.assertEqual(result["suggestions"], ["密码强度充足"])

    def test_explain_special_chars_only(self) -> None:
        password = "!@#$%"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "weak")
        self.assertEqual(
            result["suggestions"],
            ["密码长度至少 6 位（当前 5 位）", "需要包含小写字母", "需要包含大写字母", "需要包含数字"],
        )

    def test_explain_strong_with_special_chars(self) -> None:
        password = "Abc@3456"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "strong")
        self.assertEqual(result["suggestions"], ["密码强度充足"])

    def test_explain_medium_with_all_four_types(self) -> None:
        password = "Abc@34"
        result = explain_strength(password)
        _log(f"explain_strength({password!r}) -> {result}")
        self.assertEqual(result["level"], "medium")
        self.assertEqual(result["suggestions"], ["建议将密码长度增加至 8 位以上"])


class PasswordHashTests(unittest.TestCase):
    def test_hash_format(self) -> None:
        password = "hello"
        hashed = hash_password(password)
        _log(f"hash_password({password!r}) -> {hashed[:20]}... (truncated)")
        self.assertIn("$", hashed)
        salt, h = hashed.split("$", 1)
        self.assertEqual(len(salt), 32)  # 16 bytes hex
        self.assertEqual(len(h), 64)  # sha256 hex

    def test_same_password_different_hashes(self) -> None:
        password = "hello"
        h1 = hash_password(password)
        h2 = hash_password(password)
        _log(f"hash_password({password!r}) -> h1={h1[:16]}..., h2={h2[:16]}... (different salts)")
        self.assertNotEqual(h1, h2)

    def test_verify_correct(self) -> None:
        password = "mypassword"
        hashed = hash_password(password)
        ok = verify_password(password, hashed)
        _log(f"verify_password({password!r}, hash) -> {ok}")
        self.assertTrue(ok)

    def test_verify_incorrect(self) -> None:
        password = "mypassword"
        wrong = "wrong"
        hashed = hash_password(password)
        ok = verify_password(wrong, hashed)
        _log(f"verify_password({wrong!r}, hash) -> {ok}")
        self.assertFalse(ok)

    def test_verify_empty_password(self) -> None:
        password = ""
        hashed = hash_password(password)
        ok = verify_password(password, hashed)
        _log(f"verify_password({password!r}, hash) -> {ok}")
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
