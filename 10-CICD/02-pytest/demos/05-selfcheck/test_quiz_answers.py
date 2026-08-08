"""Demo for 05-自测题.md：用 pytest 自测「你是否答对概念」。

先自己做 05-自测题.md，再跑本文件核对。
改 YOUR_* 变量为你的答案后执行：pytest -v
"""

# ---------- 把下面改成你的答案，再 pytest -v ----------
YOUR_A1_EXIT_NONZERO = None  # True / False：失败时退出码是否非 0
YOUR_A1_JOB_FAILS = None  # True / False：GitLab Job 是否失败

YOUR_A2_FILE_PATTERNS = []  # 例如 ["test_*.py", "*_test.py"]

YOUR_A3_FLAG = ""  # 只跑 marker 的命令行参数，例如 "-m"

YOUR_A4_TRIGGER = ""  # CI 里决定何时跑的关键字，例如 "rules"
YOUR_A4_CASE_SELECTORS = []  # 决定跑哪批 case，例如 ["目录", "marker"]


def test_a1_exit_code_and_job():
    assert YOUR_A1_EXIT_NONZERO is True, "失败时退出码应非 0"
    assert YOUR_A1_JOB_FAILS is True, "非 0 时 Job 应失败"


def test_a2_discovery_patterns():
    expected = {"test_*.py", "*_test.py"}
    got = set(YOUR_A2_FILE_PATTERNS)
    assert got == expected, f"期望 {expected}，你写的是 {got}"


def test_a3_marker_flag():
    assert YOUR_A3_FLAG.strip() == "-m"


def test_a4_split_trigger_and_cases():
    assert YOUR_A4_TRIGGER.strip().lower() == "rules"
    normalized = {x.strip().lower() for x in YOUR_A4_CASE_SELECTORS}
    # 接受中英常见写法
    ok = normalized == {"目录", "marker"} or normalized == {"path", "marker"} or normalized == {
        "directory",
        "marker",
    }
    assert ok, "应为：rules + 目录/marker（或 path/marker）"
