# Encrypt password implementation report

## Completed tasks
- 新增 `hash_password(password: str) -> str` — 使用 `os.urandom(16).hex()` 生成 32 字符 hex 盐值，`hashlib.sha256` 哈希，返回 `salt$hash` 格式
- 新增 `verify_password(password: str, hashed: str) -> bool` — 从 `salt$hash` 中提取盐值，校验密码
- 5 个测试用例覆盖 hash 格式、不同盐值结果不同、正确/错误验证、空密码验证

## Files changed
- `app/password.py` — 新增 `hash_password` 和 `verify_password` 函数
- `tests/test_password.py` — 新增 `PasswordHashTests` 测试类（5 个测试）

## Validation result
- `python scripts/validate.py`: **PASS** (25/25 tests pass)
