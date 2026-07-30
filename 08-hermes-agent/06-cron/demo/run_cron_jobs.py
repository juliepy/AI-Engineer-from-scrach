#!/usr/bin/env python3
"""Run real Hermes cron job-store APIs — no source edits.

Uses the full hermes-agent checkout on PYTHONPATH.
Isolates writes under a temp HERMES_HOME so your real ~/.hermes is untouched.
Does NOT spawn AIAgent / gateway (no API key required).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent
EXPORTS = DEMO_ROOT / "exports" / "cron_jobs"
MODULE_ROOT = DEMO_ROOT.parent  # 06-cron/


def _resolve_hermes_agent_root() -> Path:
    env = os.environ.get("HERMES_AGENT_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "cron" / "jobs.py").is_file():
            return p
        raise SystemExit(f"HERMES_AGENT_ROOT={p} missing cron/jobs.py")

    candidates = [
        MODULE_ROOT.parents[2] / "hermes-agent",
        MODULE_ROOT.parents[1] / "hermes-agent",
        Path.home() / "hermes-agent",
    ]
    for c in candidates:
        if (c / "cron" / "jobs.py").is_file():
            return c.resolve()
    raise SystemExit(
        "Cannot find hermes-agent. Set HERMES_AGENT_ROOT to the repo root "
        "(directory that contains cron/jobs.py)."
    )


def main() -> int:
    root = _resolve_hermes_agent_root()
    sys.path.insert(0, str(root))

    tmp = Path(tempfile.mkdtemp(prefix="hermes-cron-demo-"))
    hermes_home = tmp / ".hermes"
    hermes_home.mkdir(parents=True)
    os.environ["HERMES_HOME"] = str(hermes_home)

    # Import AFTER HERMES_HOME is set — paths resolve via get_hermes_home()
    from cron.jobs import (
        JOBS_FILE,
        create_job,
        get_due_jobs,
        list_jobs,
        parse_schedule,
        pause_job,
        remove_job,
    )

    probes: list[dict] = []

    # 1) parse_schedule matrix
    schedule_cases = [
        "30m",
        "every 2h",
        "0 9 * * *",
        "2026-06-01T09:00:00",
    ]
    for s in schedule_cases:
        try:
            parsed = parse_schedule(s)
            probes.append({"op": "parse_schedule", "input": s, "ok": True, "parsed": parsed})
            print(f"parse_schedule({s!r}) → {parsed.get('kind')} / {parsed.get('display')}")
        except Exception as e:
            probes.append({"op": "parse_schedule", "input": s, "ok": False, "error": str(e)})
            print(f"parse_schedule({s!r}) FAILED: {e}")

    # 2) create jobs into temp store
    job_once = create_job(
        prompt="Demo one-shot: say hello",
        schedule="5m",
        name="demo-once",
        deliver="local",
    )
    job_every = create_job(
        prompt="Demo interval: summarize inbox",
        schedule="every 30m",
        name="demo-every",
        deliver="local",
        enabled_toolsets=["terminal", "file"],
    )
    probes.append(
        {
            "op": "create_job",
            "jobs": [
                {"id": job_once["id"], "name": job_once.get("name"), "schedule": job_once.get("schedule")},
                {"id": job_every["id"], "name": job_every.get("name"), "schedule": job_every.get("schedule")},
            ],
            "jobs_file": str(JOBS_FILE),
        }
    )
    print(f"JOBS_FILE={JOBS_FILE}")
    print(f"created: {job_once['id']} ({job_once.get('name')}), {job_every['id']} ({job_every.get('name')})")

    # 3) list / pause / due
    listed = list_jobs(include_disabled=True)
    probes.append({"op": "list_jobs", "count": len(listed), "ids": [j["id"] for j in listed]})
    print(f"list_jobs → {len(listed)} job(s)")

    pause_job(job_once["id"])
    due = get_due_jobs()
    probes.append(
        {
            "op": "get_due_jobs_after_pause",
            "due_ids": [j["id"] for j in due],
            "paused": job_once["id"],
        }
    )
    print(f"get_due_jobs (after pause once) → {[j['id'] for j in due]}")

    remove_job(job_once["id"])
    remove_job(job_every["id"])
    probes.append({"op": "cleanup", "removed": [job_once["id"], job_every["id"]]})

    EXPORTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hermes_agent_root": str(root),
        "temp_hermes_home": str(hermes_home),
        "source": "cron/jobs.py (unmodified)",
        "note": "No AIAgent / tick execution — store + schedule only",
        "probes": probes,
    }
    (EXPORTS / "00_raw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Cron jobs demo (store only)",
        "",
        f"- hermes_agent_root: `{root}`",
        f"- temp HERMES_HOME: `{hermes_home}`",
        f"- source: `cron/jobs.py` (unmodified)",
        f"- generated: {payload['generated_at']}",
        "",
        "## What this proves",
        "",
        "1. `parse_schedule` accepts duration / every / cron / ISO.",
        "2. `create_job` writes profile-scoped `jobs.json` under `HERMES_HOME`.",
        "3. `list_jobs` / `pause_job` / `get_due_jobs` operate on that store.",
        "",
        "Gateway `tick()` + `run_job()` need a live gateway / model — out of scope here.",
        "",
        "## Probes",
        "",
        "```json",
        json.dumps(probes, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    (EXPORTS / "01_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {EXPORTS / '01_report.md'}")

    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
