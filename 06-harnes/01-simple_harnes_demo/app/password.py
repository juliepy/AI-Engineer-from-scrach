import hashlib
import os
from typing import Literal

Strength = Literal["weak", "medium", "strong"]


def check_strength(password: str) -> Strength:
    """Return password strength: weak, medium, or strong."""
    if not password:
        return "weak"

    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    kinds = sum([has_lower, has_upper, has_digit, has_special])

    if length < 6 or kinds < 2:
        return "weak"
    if length >= 8 and kinds >= 3:
        return "strong"
    return "medium"


def explain_strength(password: str) -> dict:
    """Return password strength level and Chinese improvement suggestions.

    Returns a dict with keys:
        level:       Strength level ("weak", "medium", or "strong").
        suggestions: List of Chinese suggestion strings, ordered by priority.
    """
    strength = check_strength(password)

    if strength == "strong":
        return {"level": "strong", "suggestions": ["密码强度充足"]}

    if not password:
        return {"level": "weak", "suggestions": ["密码不能为空"]}

    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    suggestions: list[str] = []

    if length < 6:
        suggestions.append(f"密码长度至少 6 位（当前 {length} 位）")

    if not has_lower:
        suggestions.append("需要包含小写字母")
    if not has_upper:
        suggestions.append("需要包含大写字母")
    if not has_digit:
        suggestions.append("需要包含数字")
    if not has_special:
        suggestions.append("需要包含特殊字符")

    if strength == "medium" and length < 8:
        suggestions.append("建议将密码长度增加至 8 位以上")

    return {"level": strength, "suggestions": suggestions}


def hash_password(password: str) -> str:
    """Hash a password with a random salt using SHA-256.

    Returns a string in the format ``salt$hash`` where both values are hex.
    """
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${h}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash produced by ``hash_password``."""
    salt, expected = hashed.split("$", 1)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return h == expected
