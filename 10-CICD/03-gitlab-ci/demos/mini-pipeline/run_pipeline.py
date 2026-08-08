#!/usr/bin/env python3
"""Local GitLab CI simulator — full textbook pipeline + multi-gate variants.

Standard (default) stages:

  trigger/checkout → lint → scan → test → build → archive

Usage:
  python run_pipeline.py                 # full standard path (recommended)
  python run_pipeline.py --gate standard
  python run_pipeline.py --gate mr_fast  # multi-gate: MR fast path only
  python run_pipeline.py --gate gate1
  python run_pipeline.py --gate daily
  python run_pipeline.py --gate release
  python run_pipeline.py --all           # standard + all multi-gate variants
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
DIST = ROOT / "dist"

# Textbook full path — matches 03-标准流水线流程.md
STANDARD_JOBS = [
    "checkout",  # includes simulated MR trigger + code pull
    "lint",
    "scan",
    "unit_test",
    "build_pkg",
    "archive",
]

GATES = {
    "standard": {
        "title": "Standard full pipeline (textbook: MR → archive)",
        "jobs": STANDARD_JOBS,
    },
    "mr_fast": {
        "title": "Multi-gate MR fast path (rules: merge_request_event)",
        "jobs": ["checkout", "lint", "unit_test"],
    },
    "gate1": {
        "title": "Multi-gate Gate1 (rules: push to main)",
        "jobs": ["checkout", "lint", "scan", "gate1_critical", "build_pkg", "archive"],
    },
    "daily": {
        "title": "Multi-gate Daily (rules: schedule)",
        "jobs": ["checkout", "lint", "scan", "daily_full", "archive"],
    },
    "release": {
        "title": "Multi-gate Release (rules: tag)",
        "jobs": ["checkout", "lint", "scan", "build_pkg", "release_accept", "archive"],
    },
}


def banner(msg: str) -> None:
    line = "=" * 60
    print(f"\n{line}\n{msg}\n{line}")


def run(cmd: list[str], job: str) -> int:
    print(f"\n── Job: {job}")
    print(f"$ {' '.join(cmd)}")
    t0 = time.time()
    env = os.environ.copy()
    sep = ";" if sys.platform == "win32" else ":"
    env["PYTHONPATH"] = str(ROOT) + (sep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run(cmd, cwd=ROOT, env=env)
    elapsed = time.time() - t0
    status = "SUCCESS" if proc.returncode == 0 else "FAILED"
    print(f"← {job}: {status} ({elapsed:.1f}s, exit={proc.returncode})")
    return proc.returncode


def job_checkout() -> int:
    return run([sys.executable, "scripts/checkout_sim.py"], "checkout")


def job_lint() -> int:
    # Same as .gitlab-ci.yml lint_job script (python -m ruff ...)
    return run([sys.executable, "-m", "ruff", "check", "app", "tests", "scripts"], "lint")


def job_scan() -> int:
    return run([sys.executable, "scripts/scan.py"], "scan")


def job_pytest(path: str, marker: str, report_name: str, job: str) -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    report = ARTIFACTS / report_name
    return run(
        [
            sys.executable,
            "-m",
            "pytest",
            path,
            "-m",
            marker,
            "-v",
            f"--junitxml={report.as_posix()}",
        ],
        job,
    )


def job_build() -> int:
    DIST.mkdir(exist_ok=True)
    code = run([sys.executable, "scripts/build.py"], "build_pkg")
    if code == 0:
        ARTIFACTS.mkdir(exist_ok=True)
        for pkg in DIST.glob("mini-app-*.txt"):
            shutil.copy2(pkg, ARTIFACTS / pkg.name)
            print(f"[artifacts] {ARTIFACTS / pkg.name}")
    return code


def job_archive() -> int:
    return run([sys.executable, "scripts/archive.py"], "archive")


JOB_FUNCS = {
    "checkout": job_checkout,
    "lint": job_lint,
    "scan": job_scan,
    "unit_test": lambda: job_pytest(
        "tests/smoke", "smoke", "report-standard.xml", "unit_test"
    ),
    "mr_smoke": lambda: job_pytest("tests/smoke", "smoke", "report-mr.xml", "mr_smoke"),
    "gate1_critical": lambda: job_pytest(
        "tests/gate1", "gate1", "report-gate1.xml", "gate1_critical"
    ),
    "daily_full": lambda: job_pytest("tests/full", "full", "report-daily.xml", "daily_full"),
    "build_pkg": job_build,
    "release_accept": lambda: job_pytest(
        "tests/release", "release", "report-release.xml", "release_accept"
    ),
    "archive": job_archive,
}


def run_gate(gate: str) -> int:
    cfg = GATES[gate]
    banner(f"Pipeline: {cfg['title']}")
    print(f"Jobs: {' → '.join(cfg['jobs'])}")
    for name in cfg["jobs"]:
        code = JOB_FUNCS[name]()
        if code != 0:
            banner(f"PIPELINE FAILED at job '{name}' (gate={gate})")
            return code
    banner(f"PIPELINE PASSED (gate={gate})")
    print(f"Artifacts dir: {ARTIFACTS}")
    if ARTIFACTS.exists():
        for p in sorted(ARTIFACTS.rglob("*")):
            if p.is_file():
                print(f"  - {p.relative_to(ARTIFACTS).as_posix()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run mini-pipeline locally (full textbook path by default)"
    )
    parser.add_argument(
        "--gate",
        choices=list(GATES),
        default="standard",
        help="Which pipeline to simulate (default: standard = full textbook flow)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run standard, then mr_fast / gate1 / daily / release",
    )
    args = parser.parse_args()

    print(f"Working directory: {ROOT}")
    print(f"Python: {sys.executable}")
    print("Textbook map: trigger → checkout → lint → scan → test → build → archive")

    if args.all:
        for gate in ("standard", "mr_fast", "gate1", "daily", "release"):
            code = run_gate(gate)
            if code != 0:
                return code
        banner("ALL PIPELINES PASSED")
        return 0

    return run_gate(args.gate)


if __name__ == "__main__":
    raise SystemExit(main())
