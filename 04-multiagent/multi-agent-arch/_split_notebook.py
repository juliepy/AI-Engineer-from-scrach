"""One-off script: split 01_multi_agent_arch_demo.ipynb into 01.1–01.7."""
import json
from copy import deepcopy
from pathlib import Path

SRC = Path("01_multi_agent_arch_demo.ipynb")
OUT_DIR = Path(".")

# cell ranges: (start, end) inclusive — content cells only (excludes global title cell 0)
SPLITS = [
    ("01.1_monolithic_agent.ipynb", "01.1 · 单体 Agent 的局限", 2, 5),
    ("01.2_pipeline.ipynb", "01.2 · Pipeline 模式", 6, 10),
    ("01.3_hub_and_spoke.ipynb", "01.3 · Hub-and-Spoke 模式", 11, 14),
    ("01.4_blackboard.ipynb", "01.4 · Blackboard 模式", 15, 18),
    ("01.5_idempotency.ipynb", "01.5 · 幂等设计", 19, 21),
    ("01.6_observability.ipynb", "01.6 · 可观测性", 22, 24),
    ("01.7_graceful_degradation.ipynb", "01.7 · 优雅降级", 25, 27),
]

NAV = [
    ("01.1_monolithic_agent.ipynb", "01.1 单体 Agent"),
    ("01.2_pipeline.ipynb", "01.2 Pipeline"),
    ("01.3_hub_and_spoke.ipynb", "01.3 Hub-and-Spoke"),
    ("01.4_blackboard.ipynb", "01.4 Blackboard"),
    ("01.5_idempotency.ipynb", "01.5 幂等设计"),
    ("01.6_observability.ipynb", "01.6 可观测性"),
    ("01.7_graceful_degradation.ipynb", "01.7 优雅降级"),
]

with SRC.open(encoding="utf-8") as f:
    src_nb = json.load(f)

setup_cell = deepcopy(src_nb["cells"][1])
metadata = deepcopy(src_nb.get("metadata", {}))
nbformat = src_nb.get("nbformat", 4)
nbformat_minor = src_nb.get("nbformat_minor", 5)


def make_nav(current_file: str) -> str:
    lines = ["| 上一节 | 目录 | 下一节 |", "|--------|------|--------|"]
    idx = next(i for i, (fn, _) in enumerate(NAV) if fn == current_file)
    prev_link = f"[{NAV[idx-1][1]}]({NAV[idx-1][0]})" if idx > 0 else "—"
    next_link = f"[{NAV[idx+1][1]}]({NAV[idx+1][0]})" if idx < len(NAV) - 1 else "—"
    toc = " · ".join(
        f"**{label}**" if fn == current_file else f"[{label}]({fn})"
        for fn, label in NAV
    )
    lines.append(f"| {prev_link} | {toc} | {next_link} |")
    return "\n".join(lines)


def clean_cell(cell: dict) -> dict:
    c = deepcopy(cell)
    c.pop("execution_count", None)
    c["outputs"] = []
    return c


for filename, title, start, end in SPLITS:
    nav_md = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            f"# {title}\n",
            "\n",
            "> **01 多 Agent 架构模式** · 纯 Python 标准库 Demo\n",
            "\n",
            make_nav(filename) + "\n",
        ],
    }
    cells = [nav_md, deepcopy(setup_cell)]
    for i in range(start, end + 1):
        cells.append(clean_cell(src_nb["cells"][i]))

    out_nb = {
        "cells": cells,
        "metadata": metadata,
        "nbformat": nbformat,
        "nbformat_minor": nbformat_minor,
    }
    out_path = OUT_DIR / filename
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out_nb, f, ensure_ascii=False, indent=1)
    print(f"Wrote {filename} ({len(cells)} cells)")

print("Done.")
