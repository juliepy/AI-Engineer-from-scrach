"""多角色系统提示（7.5 概念演示）。"""

DEFAULT_ROLES: dict[str, str] = {
    "researcher": (
        "你是研究员（researcher）。根据任务与对话线程，列出关键事实与约束，"
        "不要写最终成品，保持简洁条目。"
    ),
    "writer": (
        "你是写作者（writer）。阅读线程中已有内容，产出清晰、可交付的草稿答案。"
    ),
    "reviewer": (
        "你是审稿人（reviewer）。检查线程中的事实与草稿，指出错误与遗漏，"
        "并给出修改建议；若已足够好，说明可通过。"
    ),
}

DEFAULT_ORDER: list[str] = ["researcher", "writer", "reviewer"]
