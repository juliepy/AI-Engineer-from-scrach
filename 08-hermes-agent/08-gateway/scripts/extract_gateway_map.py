#!/usr/bin/env python3
"""Refresh 08-gateway/hermes_src excerpts + catalog stubs from full hermes-agent.

Prefer the full local checkout:
  ../../../../hermes-agent   (面试狂魔/人工智能面试题/hermes-agent)

Usage (from 08-gateway/):
  python scripts/extract_gateway_map.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hermes_src"
CATALOG = ROOT / "catalog"

FULL_REPO = ROOT.parents[2] / "hermes-agent"
if not FULL_REPO.is_dir():
    FULL_REPO = Path(r"D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent")

COPY_FULL = [
    "gateway/__init__.py",
    "gateway/platform_registry.py",
    "gateway/delivery.py",
    "gateway/session_context.py",
    "gateway/config.py",
    "gateway/session.py",
    "gateway/platforms/ADDING_A_PLATFORM.md",
]

EXCERPTS: list[tuple[str, str, str, list[tuple[int, int]]]] = [
    (
        "gateway/platforms/base.py",
        "base_handle_message.py",
        "Adapter message entry + active-session guard",
        [(2253, 2360), (4585, 4780), (4808, 4920)],
    ),
    (
        "gateway/run.py",
        "run_message_and_cron.py",
        "Runner message pipeline + cron boot",
        [(2775, 2980), (8853, 8980), (10773, 10850), (20324, 20410), (20816, 20890)],
    ),
    (
        "gateway/run.py",
        "run_busy_session.py",
        "Runner busy-session guard (level 2)",
        [(5360, 5570)],
    ),
    (
        "hermes_cli/commands.py",
        "commands_bypass.py",
        "GATEWAY_KNOWN_COMMANDS + should_bypass_active_session",
        [(330, 420)],
    ),
    (
        "gateway/session.py",
        "session_key_store.py",
        "Session key + store",
        [(148, 330), (871, 960), (1775, 1860)],
    ),
    (
        "gateway/delivery.py",
        "delivery_router.py",
        "DeliveryRouter.deliver",
        [(1, 80), (222, 320)],
    ),
    (
        "gateway/config.py",
        "config_platform_home.py",
        "Platform / HomeChannel / GatewayConfig",
        [(212, 360), (444, 540), (655, 780)],
    ),
]


def excerpt(rel: str, out_name: str, header: str, ranges: list[tuple[int, int]]) -> None:
    lines = (FULL_REPO / rel).read_text(encoding="utf-8", errors="replace").splitlines(True)
    parts = [f"# Excerpt from {rel}\n# {header}\n\n"]
    for a, b in ranges:
        parts.append(f"# ===== lines {a}-{b} =====\n")
        parts.extend(lines[a - 1 : b])
        parts.append("\n")
    out = SRC / "gateway" / "excerpts" / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(parts), encoding="utf-8")
    print(f"excerpt {out_name}")


def main() -> None:
    if not FULL_REPO.is_dir():
        raise SystemExit(f"hermes-agent not found: {FULL_REPO}")

    for rel in COPY_FULL:
        src = FULL_REPO / rel
        if not src.is_file():
            print(f"skip missing {rel}")
            continue
        dst = SRC / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"copied {rel}")

    for rel, out_name, header, ranges in EXCERPTS:
        excerpt(rel, out_name, header, ranges)

    print(f"OK — hermes_src refreshed from {FULL_REPO}")
    print("Catalog markdown is hand-authored under catalog/; re-read notes after refresh.")


if __name__ == "__main__":
    main()
