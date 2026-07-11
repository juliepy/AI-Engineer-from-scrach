# explain-strength plan

## Scope

在现有 `check_strength()` 基础上，新增 `explain_strength(password)` 函数。

- **输入**：密码字符串
- **输出**：字典，包含两个字段：
  - `level`：`"weak"` / `"medium"` / `"strong"`（复用 `check_strength()` 的判定结果）
  - `suggestions`：中文改进建议列表（字符串数组）
- **建议规则**（仅列出未满足的条件，已满足的不出现在列表中）：
  - 长度 < 6 → `"密码至少 6 位"`
  - 缺少小写字母 → `"缺少小写字母"`
  - 缺少大写字母 → `"缺少大写字母"`
  - 缺少数字 → `"缺少数字"`
  - 长度 ≥ 6 但未达到 strong（长度 < 8 或字符类型不全）→ `"建议长度至少 8 位且同时包含大写、小写、数字"`
- **不影响**现有 `check_strength()` 的行为和已有测试

## Affected files

- `app/password.py` — 新增 `explain_strength()` 及必要的辅助逻辑
- `tests/test_password.py` — 新增针对 `explain_strength()` 的测试用例

## Tasks

- [ ] 在 `app/password.py` 中定义返回类型（如 `TypedDict` 或普通 `dict`），并实现 `explain_strength(password: str) -> dict`
- [ ] `explain_strength` 内部调用 `check_strength()` 获取 `level`，再根据密码内容生成 `suggestions` 列表
- [ ] 确保 strong 密码（如 `"Abc12345"`）返回空的 `suggestions` 列表
- [ ] 在 `tests/test_password.py` 中新增测试：`"abc"` 返回 weak 且 suggestions 包含长度、大写、数字相关建议
- [ ] 在 `tests/test_password.py` 中新增测试：`"Abc12345"` 返回 strong 且 `suggestions` 为空列表
- [ ] 在 `tests/test_password.py` 中新增测试：现有 `check_strength` 的 5 个测试仍然全部通过（不修改、不破坏）
- [ ] 运行 `python scripts/validate.py`，确认全部测试通过

## Example outputs

```python
explain_strength("abc")
# {"level": "weak", "suggestions": ["密码至少 6 位", "缺少大写字母", "缺少数字"]}

explain_strength("abc123")
# {"level": "medium", "suggestions": ["缺少大写字母", "建议长度至少 8 位且同时包含大写、小写、数字"]}

explain_strength("Abc12345")
# {"level": "strong", "suggestions": []}
```

## Validation

```bash
python scripts/validate.py
```

Done means: command exits with code 0 and prints `validate: PASS`.
