# Encrypt password plan

## Scope
为 `app/password.py` 增加密码加密（hash）与验证功能，使用内置 `hashlib` 库，采用 SHA-256 + 随机盐值。

## Tasks
- [ ] **`app/password.py`** — 新增 `hash_password(password: str) -> str` 函数（返回 `salt$hash` 格式）和 `verify_password(password: str, hashed: str) -> bool` 函数
- [ ] **`tests/test_password.py`** — 为 `hash_password` 和 `verify_password` 增加测试用例（hash 格式、相同密码不同盐值结果不同、正确/错误密码验证）
- [ ] 运行 `python scripts/validate.py` 验证所有测试通过

## Affected files
- `app/password.py` — 新增两个函数
- `tests/test_password.py` — 新增测试类

## Validation
- `python scripts/validate.py`
