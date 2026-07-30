"""EXCERPT for teaching — not a runnable module.

Pulled from cron/scheduler.py (full file lives beside this excerpt).
Focus: _resolve_cron_disabled_toolsets, SILENT_MARKER, run_job (no_agent + skip_memory),
       tick (lock + get_due_jobs + advance_next_run + parallel).

Open the full scheduler.py for line-accurate debugging.
"""

# --- scheduler.py L117-L201 ---
def _resolve_cron_disabled_toolsets(cfg: dict) -> list[str]:
    """Toolsets a cron-spawned agent must never receive.

    Three protected toolsets are always disabled in cron context:
      - ``cronjob`` 鈥?would let a cron-spawned agent schedule more cron jobs
      - ``messaging`` 鈥?interactive, needs a live gateway session
      - ``clarify`` 鈥?interactive, blocks waiting for user input

    User-level ``agent.disabled_toolsets`` from config.yaml is layered on top
    so per-job ``enabled_toolsets`` cannot bypass policy that applies to
    ordinary agent runs (#25752 鈥?LLM-supplied enabled_toolsets was widening
    past config.yaml's denylist).
    """
    disabled = ["cronjob", "messaging", "clarify"]
    agent_cfg = (cfg or {}).get("agent") or {}
    user_disabled = agent_cfg.get("disabled_toolsets") or []
    for name in user_disabled:
        name = str(name).strip()
        if name and name not in disabled:
            disabled.append(name)
    return disabled


def _merge_mcp_into_per_job_toolsets(per_job: list[str], cfg: dict) -> list[str]:
    """Layer enabled MCP servers onto a per-job ``enabled_toolsets`` allowlist.

    A per-job list scopes the *native* toolsets, but on its own it silently
    drops every MCP server: ``discover_mcp_tools()`` registers the tools into
    the global registry, yet ``get_tool_definitions(enabled_toolsets=...)``
    only keeps toolsets named in the list. The agent then rejects every
    ``mcp_*`` call with "Unknown tool". This restores parity with
    ``_get_platform_tools`` MCP semantics:

      * ``no_mcp`` sentinel present  -> no MCP servers (sentinel stripped)
      * one or more MCP server names already listed -> treat as an allowlist,
        add nothing further (the user named exactly the servers they want)
      * otherwise -> union in every globally-enabled MCP server
    """
    result = [t for t in per_job if t != "no_mcp"]
    if "no_mcp" in per_job:
        return result
    # lazy import: avoid heavy hermes_cli import at cron module load (matches
    # _resolve_cron_enabled_toolsets' fallback) and share one MCP-membership
    # computation with the gateway/CLI platform resolver.
    from hermes_cli.tools_config import enabled_mcp_server_names
    enabled_mcp = enabled_mcp_server_names(cfg)
    if set(result) & enabled_mcp:
        return result
    for name in sorted(enabled_mcp):
        if name not in result:
            result.append(name)
    return result


def _resolve_cron_enabled_toolsets(job: dict, cfg: dict) -> list[str] | None:
    """Resolve the toolset list for a cron job.

    Precedence:
    1. Per-job ``enabled_toolsets`` (set via ``cronjob`` tool on create/update).
       Keeps the agent's job-scoped toolset override intact 鈥?#6130. Enabled
       MCP servers are layered on per ``_merge_mcp_into_per_job_toolsets`` so a
       native-toolset allowlist does not silently strip MCP tools.
    2. Per-platform ``hermes tools`` config for the ``cron`` platform.
       Mirrors gateway behavior (``_get_platform_tools(cfg, platform_key)``)
       so users can gate cron toolsets globally without recreating every job.
    3. ``None`` on any lookup failure 鈥?AIAgent loads the full default set
       (legacy behavior before this change, preserved as the safety net).

    _DEFAULT_OFF_TOOLSETS ({moa, homeassistant, rl}) are removed by
    ``_get_platform_tools`` for unconfigured platforms, so fresh installs
    get cron WITHOUT ``moa`` by default (issue reported by Norbert 鈥?
    surprise $4.63 run).
    """
    per_job = job.get("enabled_toolsets")
    if per_job:
        return _merge_mcp_into_per_job_toolsets(list(per_job), cfg or {})
    try:
        from hermes_cli.tools_config import _get_platform_tools  # lazy: avoid heavy import at cron module load
        return sorted(_get_platform_tools(cfg or {}, "cron"))
    except Exception as exc:
        logger.warning(
            "Cron toolset resolution failed, falling back to full default toolset: %s",
            exc,
        )
        return None

# --- scheduler.py L243-L255 ---
# Sentinel: when a cron agent has nothing new to report, it can start its
# response with this marker to suppress delivery.  Output is still saved
# locally for audit.
SILENT_MARKER = "[SILENT]"

# Canonical silence tokens recognized in cron output.  Cron's contract is
# intentionally looser than the gateway's exact-whole-response rule: the cron
# system prompt *instructs* the agent to emit "[SILENT]", and real agents often
# bracket it with a short note or trailing newline.  We therefore suppress when
# a marker is the entire response OR appears as its own first/last line 鈥?but
# NOT when a token merely appears mid-sentence in a genuine report (e.g.
# "I considered staying [SILENT] but here is the summary鈥? must deliver).
_CRON_SILENCE_TOKENS = frozenset({"[SILENT]", "SILENT", "NO_REPLY", "NO REPLY"})

# --- scheduler.py L2485-L2610 ---
def run_job(
    job: dict, *, defer_agent_teardown: Optional[list] = None
) -> tuple[bool, str, str, Optional[str]]:
    """
    Execute a single cron job.

    ``defer_agent_teardown``: when a caller passes a list, ``run_job`` skips
    the agent's async-resource teardown (``agent.close()`` +
    ``cleanup_stale_async_clients()``) in its ``finally`` block and instead
    appends the live agent to that list. The caller is then responsible for
    calling ``_teardown_cron_agent(agent)`` AFTER it has delivered the result.
    This closes the ordering window in #58720 where delivery ran against a
    torn-down async client (defense-in-depth alongside the interpreter-shutdown
    guard). When ``None`` (the default) teardown happens inline as before, so
    every existing caller is unchanged.

    Returns:
        Tuple of (success, full_output_doc, final_response, error_message)
    """
    job_id = job["id"]
    job_name = str(job.get("name") or job.get("prompt") or job_id or "cron job")

    # ---------------------------------------------------------------
    # no_agent short-circuit 鈥?the script IS the job, no LLM involvement.
    # ---------------------------------------------------------------
    # This mirrors the classic "run a bash script on a timer, send its
    # stdout to telegram" watchdog pattern. The agent path is skipped
    # entirely: no AIAgent, no prompt, no tool loop, no token spend.
    #
    # We check this BEFORE importing run_agent / constructing SessionDB so
    # a pure-script tick never pays for the agent machinery it isn't going
    # to use. Keep this block self-contained.
    #
    # Semantics:
    #   - script stdout (trimmed) 鈫?delivered verbatim as the final message
    #   - empty stdout            鈫?silent run (no delivery, success=True)
    #   - non-zero exit / timeout 鈫?delivered as an error alert, success=False
    #   - wakeAgent=false gate    鈫?treated like empty stdout (silent), since
    #                               the whole point of no_agent is that there
    #                               is no agent to wake
    if job.get("no_agent"):
        script_path = job.get("script")
        if not script_path:
            err = "no_agent=True but no script is set for this job"
            logger.error("Job '%s': %s", job_id, err)
            return False, "", "", err

        # Apply workdir if configured 鈥?lets scripts use predictable relative
        # paths. For no_agent jobs this is just the subprocess cwd (not an
        # agent TERMINAL_CWD bridge).
        _job_workdir = (job.get("workdir") or "").strip() or None
        _prior_cwd = None
        if _job_workdir and Path(_job_workdir).is_dir():
            _prior_cwd = os.getcwd()
            try:
                os.chdir(_job_workdir)
            except OSError:
                _prior_cwd = None

        try:
            ok, output = _run_job_script(script_path)
        finally:
            if _prior_cwd is not None:
                try:
                    os.chdir(_prior_cwd)
                except OSError:
                    pass

        now_iso = _hermes_now().strftime("%Y-%m-%d %H:%M:%S")

        if not ok:
            # Script crashed / timed out / exited non-zero.  Deliver the
            # error so the user knows the watchdog itself broke 鈥?silent
            # failure for an alerting job is the worst-case outcome.
            alert = (
                f"鈿?Cron watchdog '{job_name}' script failed\n\n"
                f"{output}\n\n"
                f"Time: {now_iso}"
            )
            doc = (
                f"# Cron Job: {job_name}\n\n"
                f"**Job ID:** {job_id}\n"
                f"**Run Time:** {now_iso}\n"
                f"**Mode:** no_agent (script)\n"
                f"**Status:** script failed\n\n"
                f"{output}\n"
            )
            return False, doc, alert, output

        # Honour the wakeAgent gate as a silent signal 鈥?`wakeAgent: false`
        # means "nothing to report this tick", same as empty stdout.
        if not _parse_wake_gate(output):
            logger.info(
                "Job '%s' (no_agent): wakeAgent=false gate 鈥?silent run", job_id
            )
            silent_doc = (
                f"# Cron Job: {job_name}\n\n"
                f"**Job ID:** {job_id}\n"
                f"**Run Time:** {now_iso}\n"
                f"**Mode:** no_agent (script)\n"
                f"**Status:** silent (wakeAgent=false)\n"
            )
            return True, silent_doc, SILENT_MARKER, None

        if not output.strip():
            logger.info("Job '%s' (no_agent): empty stdout 鈥?silent run", job_id)
            silent_doc = (
                f"# Cron Job: {job_name}\n\n"
                f"**Job ID:** {job_id}\n"
                f"**Run Time:** {now_iso}\n"
                f"**Mode:** no_agent (script)\n"
                f"**Status:** silent (empty output)\n"
            )
            return True, silent_doc, SILENT_MARKER, None

        doc = (
            f"# Cron Job: {job_name}\n\n"
            f"**Job ID:** {job_id}\n"
            f"**Run Time:** {now_iso}\n"
            f"**Mode:** no_agent (script)\n\n"
            f"---\n\n"
            f"{output}\n"
        )
        return True, doc, output, None

    # ---------------------------------------------------------------

# --- scheduler.py L2674-L2690 ---
    if prompt is None:
        logger.info("Job '%s': script produced no output, skipping AI call.", job_name)
        return True, "", SILENT_MARKER, None
    origin = _resolve_origin(job)
    _cron_session_id = f"cron_{job_id}_{_hermes_now().strftime('%Y%m%d_%H%M%S')}"

    logger.info("Running job '%s' (ID: %s)", job_name, job_id)
    logger.info("Prompt: %s", prompt[:100])

    agent = None

    # Mark this as a cron session so the approval system can apply cron_mode.
    # This env var is process-wide and persists for the lifetime of the
    # scheduler process 鈥?every job this process runs is a cron job.
    os.environ["HERMES_CRON_SESSION"] = "1"

    # Use ContextVars for per-job session/delivery state so parallel jobs

# --- scheduler.py L3040-L3100 ---
        except Exception as _mcp_exc:
            logger.warning(
                "Job '%s': MCP initialization failed (non-fatal): %s",
                job_id, _mcp_exc,
            )

        agent = AIAgent(
            model=model,
            api_key=runtime.get("api_key"),
            base_url=runtime.get("base_url"),
            provider=runtime.get("provider"),
            api_mode=runtime.get("api_mode"),
            acp_command=runtime.get("command"),
            acp_args=runtime.get("args"),
            max_iterations=max_iterations,
            reasoning_config=reasoning_config,
            prefill_messages=prefill_messages,
            fallback_model=fallback_model,
            credential_pool=credential_pool,
            providers_allowed=pr.get("only"),
            providers_ignored=pr.get("ignore"),
            providers_order=pr.get("order"),
            provider_sort=pr.get("sort"),
            openrouter_min_coding_score=(_cfg.get("openrouter") or {}).get("min_coding_score"),
            enabled_toolsets=_resolve_cron_enabled_toolsets(job, _cfg),
            disabled_toolsets=_resolve_cron_disabled_toolsets(_cfg),
            quiet_mode=True,
            # Cron jobs should always inherit the user's SOUL.md identity from
            # HERMES_HOME. When a workdir is configured, also inject project
            # context files (AGENTS.md / CLAUDE.md / .cursorrules) from there.
            # Without a workdir, keep cwd context discovery disabled.
            skip_context_files=not bool(_job_workdir),
            load_soul_identity=True,
            skip_memory=True,  # Cron system prompts would corrupt user representations
            platform="cron",
            session_id=_cron_session_id,
            session_db=_session_db,
        )
        
        # Run the agent with an *inactivity*-based timeout: the job can run
        # for hours if it's actively calling tools / receiving stream tokens,
        # but a hung API call or stuck tool with no activity for the configured
        # duration is caught and killed.  Default 600s (10 min inactivity);
        # override via HERMES_CRON_TIMEOUT env var.  0 = unlimited.
        #
        # Uses the agent's built-in activity tracker (updated by
        # _touch_activity() on every tool call, API call, and stream delta).
        _raw_cron_timeout = os.getenv("HERMES_CRON_TIMEOUT", "").strip()
        if _raw_cron_timeout:
            try:
                _cron_timeout = float(_raw_cron_timeout)
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid HERMES_CRON_TIMEOUT=%r; using default 600s",
                    _raw_cron_timeout,
                )
                _cron_timeout = 600.0
        else:
            _cron_timeout = 600.0
        _cron_inactivity_limit = _cron_timeout if _cron_timeout > 0 else None
        _POLL_INTERVAL = 5.0

# --- scheduler.py L3560-L3652 ---
def tick(verbose: bool = True, adapters=None, loop=None, sync: bool = True) -> int:
    """
    Check and run all due jobs.
    
    Uses a file lock so only one tick runs at a time, even if the gateway's
    in-process ticker and a standalone daemon or manual tick overlap.
    
    Args:
        verbose: Whether to print status messages
        adapters: Optional dict mapping Platform 鈫?live adapter (from gateway)
        loop: Optional asyncio event loop (from gateway) for live adapter sends
    
    Returns:
        Number of jobs executed (0 if another tick is already running)
    """
    lock_dir, lock_file = _get_lock_paths()
    lock_dir.mkdir(parents=True, exist_ok=True)

    # Cross-platform file locking: fcntl on Unix, msvcrt on Windows
    lock_fd = None
    try:
        lock_fd = open(lock_file, "w", encoding="utf-8")
        if fcntl:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        elif msvcrt:
            msvcrt.locking(lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
    except (OSError, IOError):
        logger.debug("Tick skipped 鈥?another instance holds the lock")
        if lock_fd is not None:
            lock_fd.close()
        return 0

    try:
        due_jobs = get_due_jobs()

        if verbose and not due_jobs:
            logger.info("%s - No jobs due", _hermes_now().strftime('%H:%M:%S'))
            return 0

        if verbose:
            logger.info("%s - %s job(s) due", _hermes_now().strftime('%H:%M:%S'), len(due_jobs))

        # Advance next_run_at for all recurring jobs FIRST, under the file lock,
        # before any execution begins.  This preserves at-most-once semantics.
        # For parallel jobs that are already running, advance_next_run keeps
        # bumping next_run_at forward so the grace window never expires.
        # mark_job_run() overwrites next_run_at on completion.
        for job in due_jobs:
            advance_next_run(job["id"])

        # Resolve max parallel workers: env var > config.yaml > unbounded.
        # Set HERMES_CRON_MAX_PARALLEL=1 to restore old serial behaviour.
        _max_workers: Optional[int] = None
        try:
            _env_par = os.getenv("HERMES_CRON_MAX_PARALLEL", "").strip()
            if _env_par:
                _max_workers = int(_env_par) or None
        except (ValueError, TypeError):
            logger.warning("Invalid HERMES_CRON_MAX_PARALLEL value; defaulting to unbounded")
        if _max_workers is None:
            try:
                _ucfg = load_config() or {}
                _cfg_par = (
                    _ucfg.get("cron", {}) if isinstance(_ucfg, dict) else {}
                ).get("max_parallel_jobs")
                if _cfg_par is not None:
                    _max_workers = int(_cfg_par) or None
            except Exception:
                pass

        if verbose:
            logger.info(
                "Running %d job(s) in parallel (max_workers=%s)",
                len(due_jobs),
                _max_workers if _max_workers else "unbounded",
            )

        def _process_job(job: dict) -> bool:
            """Run one due job end-to-end. Thin wrapper around the shared
            module-level ``run_one_job`` so ``tick`` and external providers
            (Chronos ``fire_due``) use the identical execute鈫抯ave鈫抎eliver鈫抦ark
            body."""
            return run_one_job(job, adapters=adapters, loop=loop, verbose=verbose)

        # Partition due jobs: those with a per-job workdir mutate
        # os.environ["TERMINAL_CWD"] inside run_job, which is process-global, so
        # they queue on the single-thread sequential pool to run one at a time.
        # That alone only keeps workdir jobs from overlapping EACH OTHER;
        # run_job's _terminal_cwd_lock is what additionally stops a concurrently
        # firing workdir-less parallel-pool job from observing the override.
        sequential_jobs = [j for j in due_jobs if (j.get("workdir") or "").strip()]
        parallel_jobs = [j for j in due_jobs if not (j.get("workdir") or "").strip()]


