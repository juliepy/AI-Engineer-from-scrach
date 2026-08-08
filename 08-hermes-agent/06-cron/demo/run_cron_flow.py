#!/usr/bin/env python3
"""Cron 全链路 demo：create → jobs.json → tick → run_job → output（省 gateway）。

对照 hermes_src/README.md。改顶部开关即可。
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent
MODULE_ROOT = DEMO_ROOT.parent
HERMES_HOME = DEMO_ROOT

# —— 开关 ——
SCHEDULE = "every 1m"  # 每 1 分钟一次（Hermes interval 最短 1m）
REPEAT = 2             # 共执行 5 次后自动删除
POLL_SECONDS = 5
RUN_NOW = False        # True：首跑立刻到期（仍按 interval 续跑）
RUN_AGENT = False      # True：再跑 AIAgent 分支


def step(n: int, msg: str) -> None:
    print(f"\n[step #{n}] {msg}")


def info(msg: str) -> None:
    print(f"  {msg}")


def _resolve_hermes_agent_root() -> Path:
    env = os.environ.get("HERMES_AGENT_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "cron" / "jobs.py").is_file():
            return p
        raise SystemExit(f"HERMES_AGENT_ROOT={p} missing cron/jobs.py")
    for c in (
        MODULE_ROOT.parents[2] / "hermes-agent",
        MODULE_ROOT.parents[1] / "hermes-agent",
        Path.home() / "hermes-agent",
    ):
        if (c / "cron" / "jobs.py").is_file():
            return c.resolve()
    raise SystemExit("Set HERMES_AGENT_ROOT to hermes-agent repo root")


def _reset_store() -> None:
    cron_dir = HERMES_HOME / "cron"
    cron_dir.mkdir(parents=True, exist_ok=True)
    for name in ("jobs.json", ".tick.lock", ".jobs.lock"):
        p = cron_dir / name
        if p.is_file():
            p.unlink()


def _past_iso(seconds_ago: int = 20) -> str:
    return (datetime.now().astimezone() - timedelta(seconds=seconds_ago)).isoformat()


def _seconds_until(next_run_at: str) -> float:
    return (datetime.fromisoformat(next_run_at) - datetime.now().astimezone()).total_seconds()


def _completed(job: dict | None) -> int:
    if job is None:
        return REPEAT
    return int((job.get("repeat") or {}).get("completed", 0))


def _list_outputs(job_id: str) -> list[Path]:
    out_dir = HERMES_HOME / "cron" / "output" / job_id
    return sorted(out_dir.glob("*.md")) if out_dir.is_dir() else []


def _latest_script_stdout(job_id: str) -> str | None:
    """读最新 output.md，只取 --- 后的脚本 stdout（如 hello）。"""
    outs = _list_outputs(job_id)
    if not outs:
        return None
    text = outs[-1].read_text(encoding="utf-8")
    if "\n---\n" in text:
        return text.split("\n---\n", 1)[1].strip()
    return text.strip() or None


def _wait_and_tick(job_id: str, tick, get_job, timeout: float) -> int:
    """轮询 tick，直到 repeat 用尽或超时。每次执行打进度 + 脚本输出。"""
    started = time.monotonic()
    total = 0
    while True:
        n = tick(verbose=False)
        total += n
        job = get_job(job_id)
        if n > 0:
            body = _latest_script_stdout(job_id)
            info(f"{_completed(job)}/{REPEAT}  → {body!r}" if body else f"{_completed(job)}/{REPEAT}")
        if job is None:
            return total
        if time.monotonic() - started > timeout:
            info(f"timeout  {_completed(job)}/{REPEAT}")
            return total
        left = _seconds_until(job["next_run_at"]) if job.get("next_run_at") else 0
        time.sleep(min(POLL_SECONDS, max(1.0, left + 0.5)))


def main() -> int:
    root = _resolve_hermes_agent_root()
    sys.path.insert(0, str(root))
    os.environ["HERMES_HOME"] = str(HERMES_HOME)
    _reset_store()

    from cron.jobs import get_job, update_job
    from cron.scheduler import tick
    from tools.cronjob_tools import cronjob

    # step #1  cronjob(create) — 只登记
    step(1, "cronjob(create)")
    create_raw = cronjob(
        action="create",
        prompt="demo note (ignored when no_agent)",
        schedule=SCHEDULE,
        name="demo-no-agent",
        deliver="local",
        script="say_hello.py",
        no_agent=True,
        repeat=REPEAT,
    )
    create = json.loads(create_raw)
    if not create.get("success"):
        info(create_raw)
        return 1
    job_id = create["job_id"]
    info(f"job_id={job_id}  repeat={create.get('repeat')}")

    # step #2  读 Job Store（确认已落盘）
    step(2, "jobs.json")
    if RUN_NOW:
        update_job(job_id, {"next_run_at": _past_iso()})
    job = get_job(job_id)
    assert job is not None
    left = _seconds_until(job["next_run_at"]) if job.get("next_run_at") else 0
    info(f"script={job.get('script')}  next≈{max(0, left):.0f}s")

    # step #3  tick 直到跑满 REPEAT
    step(3, f"tick ×{REPEAT}")
    timeout = max(0.0, left) + (REPEAT - 1) * 60.0 + 60.0
    n = _wait_and_tick(job_id, tick, get_job, timeout)
    info(f"executed={n}")

    # step #4  output 落盘汇总
    step(4, "output")
    outs = _list_outputs(job_id)
    info(f"files={len(outs)}  dir=cron/output/{job_id}/")

    # step #5  AIAgent（可选）
    if RUN_AGENT:
        step(5, "AIAgent")
        agent_raw = cronjob(
            action="create",
            prompt="用一句中文打招呼，包含单词 hello。",
            schedule=_past_iso(),
            name="demo-agent",
            deliver="local",
            enabled_toolsets=["safe"],
            no_agent=False,
        )
        agent = json.loads(agent_raw)
        if not agent.get("success"):
            info(agent_raw)
            return 1
        tick(verbose=False)
        outs2 = _list_outputs(agent["job_id"])
        if outs2:
            print(outs2[-1].read_text(encoding="utf-8").rstrip())

    print("\n[done]" if n >= REPEAT else "\n[fail]")
    return 0 if n >= REPEAT else 1


if __name__ == "__main__":
    raise SystemExit(main())
