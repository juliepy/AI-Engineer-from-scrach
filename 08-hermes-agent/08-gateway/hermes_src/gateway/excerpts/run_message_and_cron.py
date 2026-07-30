# Excerpt from gateway/run.py
# Runner message pipeline + cron boot

# ===== lines 2775-2980 =====
class GatewayRunner(GatewayAuthorizationMixin, GatewayKanbanWatchersMixin, GatewaySlashCommandsMixin):
    """
    Main gateway controller.

    Manages the lifecycle of all platform adapters and routes
    messages to/from the agent.
    """

    # Class-level defaults so partial construction in tests doesn't
    # blow up on attribute access.
    _running_agents_ts: Dict[str, float] = {}
    _busy_input_mode: str = "interrupt"
    _busy_text_mode: str = "interrupt"
    _restart_drain_timeout: float = DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT
    _exit_code: Optional[int] = None
    _draining: bool = False
    _external_drain_active: bool = False
    _restart_requested: bool = False
    _restart_task_started: bool = False
    _restart_detached: bool = False
    _restart_via_service: bool = False
    _detached_restart_helper_started: bool = False
    _restart_command_source: Optional[SessionSource] = None
    _stop_task: Optional[asyncio.Task] = None
    _restart_task: Optional[asyncio.Task] = None
    _session_model_overrides: Dict[str, Dict[str, str]] = {}
    _session_reasoning_overrides: Dict[str, Dict[str, Any]] = {}
    _startup_restore_in_progress: bool = False

    def __init__(self, config: Optional[GatewayConfig] = None):
        global _gateway_runner_ref
        self.config = config or load_gateway_config()
        # Mark the process as a profile multiplexer when configured. This flips
        # agent.secret_scope.get_secret() to fail-closed on any unscoped
        # credential read, so a missed migration crashes loudly instead of
        # leaking a cross-profile value (Workstream A). Inert when off.
        try:
            from agent.secret_scope import set_multiplex_active
            set_multiplex_active(bool(getattr(self.config, "multiplex_profiles", False)))
        except Exception:
            logger.debug("could not set multiplex-active flag", exc_info=True)
        self.adapters: Dict[Platform, BasePlatformAdapter] = {}
        # Multi-profile multiplexing: adapters for NON-default profiles live
        # here, keyed by profile name then Platform. self.adapters stays the
        # default/active profile's map so the ~93 existing self.adapters[...]
        # sites are untouched when multiplexing is off (this dict is empty).
        # Populated by _start_secondary_profile_adapters().
        self._profile_adapters: Dict[str, Dict[Platform, BasePlatformAdapter]] = {}
        self._warn_if_docker_media_delivery_is_risky()
        _gateway_runner_ref = _weakref.ref(self)

        # Load ephemeral config from config.yaml / env vars.
        # Both are injected at API-call time only and never persisted.
        self._prefill_messages = self._load_prefill_messages()
        self._ephemeral_system_prompt = self._load_ephemeral_system_prompt()
        self._reasoning_config = self._load_reasoning_config()
        self._service_tier = self._load_service_tier()
        self._show_reasoning = self._load_show_reasoning()
        self._busy_input_mode = self._load_busy_input_mode()
        self._busy_text_mode = self._load_busy_text_mode()
        self._restart_drain_timeout = self._load_restart_drain_timeout()
        self._provider_routing = self._load_provider_routing()
        self._fallback_model = self._load_fallback_model()

        # Wire process registry into session store for reset protection.
        # A background process older than the configured threshold (default 24h,
        # session_reset.bg_process_max_age_hours) is treated as stale and no
        # longer blocks session idle / daily reset — see #29177. The process is
        # NOT killed, only ignored by the reset guard.
        from tools.process_registry import process_registry
        _bg_max_age_hours = getattr(
            self.config.default_reset_policy, "bg_process_max_age_hours", 24
        )
        _bg_max_age_seconds = (
            _bg_max_age_hours * 3600 if _bg_max_age_hours and _bg_max_age_hours > 0 else None
        )
        self.session_store = SessionStore(
            self.config.sessions_dir, self.config,
            has_active_processes_fn=lambda key: process_registry.has_active_for_session(
                key, max_active_age=_bg_max_age_seconds,
            ),
        )
        # One enforced loop-side boundary for the synchronous SessionStore.
        # Sync helpers keep using ``session_store`` directly; async gateway
        # handlers call this facade and await every operation.
        self._async_session_store = AsyncSessionStore(self.session_store)
        self.delivery_router = DeliveryRouter(self.config)
        self._running = False
        self._gateway_loop: Optional[asyncio.AbstractEventLoop] = None
        self._shutdown_event = asyncio.Event()
        self._exit_cleanly = False
        self._exit_with_failure = False
        self._exit_reason: Optional[str] = None
        self._exit_code: Optional[int] = None
        self._draining = False
        # External (NAS-driven) drain state — distinct from the shutdown
        # ``_draining`` flag above. Set by ``_drain_control_watcher`` when the
        # ``.drain_request.json`` marker is present: the gateway flips
        # ``gateway_state -> draining`` and refuses NEW turns, but the process
        # does NOT exit (the whole point — quiesce-without-restart, D4a). It is
        # fully reversible: removing the marker reverts to ``running`` and
        # re-accepts turns. ``_draining`` (shutdown) is one-way and ends in
        # process exit; this one is a steady state NAS polls during its
        # request -> poll -> proceed loop.
        self._external_drain_active = False
        self._restart_requested = False
        # Set by shutdown_signal_handler when a SIGTERM/SIGINT arrived
        # WITHOUT a planned-stop / takeover marker — i.e. an unexpected
        # external signal (container/s6 SIGTERM on `docker restart` or
        # image upgrade, OOM-killer, bare `kill`). Distinct from an
        # operator-requested stop, which writes a marker first. Used by
        # _stop_impl to decide whether to persist gateway_state=stopped
        # (see issue #42675): an unexpected signal must NOT persist
        # "stopped", or container_boot refuses to auto-start the gateway
        # on the next boot.
        self._signal_initiated_shutdown = False
        self._restart_task_started = False
        self._restart_detached = False
        self._restart_via_service = False
        self._detached_restart_helper_started = False
        self._restart_command_source: Optional[SessionSource] = None
        # Monotonic-ish wall clock of when this GatewayRunner was constructed.
        # Used by the /restart redelivery guard to bound the window in which a
        # missing dedup marker is treated as a stale redelivery.
        self._startup_time: float = time.time()
        # Set True at startup when this process booted as the result of a
        # chat-originated /restart (i.e. .restart_notify.json existed on boot).
        # A one-shot signal consumed by _is_stale_restart_redelivery so the
        # marker-missing fallback only suppresses a /restart when we KNOW we
        # just came out of a restart cycle — never on a genuine fresh boot.
        self._booted_from_restart: bool = False
        self._stop_task: Optional[asyncio.Task] = None
        self._restart_task: Optional[asyncio.Task] = None
        self._executor_lock = threading.Lock()
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        # Set on gateway stop so the recreate-on-shutdown path can't resurrect
        # the pool during a real shutdown.
        self._executor_closing = False
        # Track running agents per session for interrupt support
        # Key: session_key, Value: AIAgent instance
        self._running_agents: Dict[str, Any] = {}
        self._running_agents_ts: Dict[str, float] = {}  # start timestamp per session
        self._active_session_leases: Dict[str, Any] = {}
        self._pending_messages: Dict[str, str] = {}  # Queued messages during interrupt
        # Last successfully-resolved (non-empty) model, keyed by session. Used
        # as a fallback when a fresh config read transiently returns an empty
        # model (e.g. an mtime-keyed config-cache miss during a post-interrupt
        # recovery turn). Without this, the agent is built with model="" and
        # every API call fails HTTP 400 "No models provided" — the session goes
        # silent until the user manually re-sends. See #35314. ``"*"`` holds a
        # process-wide last-known-good for sessions seen for the first time.
        self._last_resolved_model: Dict[str, str] = {}
        # Overflow buffer for explicit /queue commands.  The adapter-level
        # _pending_messages dict is a single slot per session (designed for
        # "next-turn" follow-ups where repeated sends collapse into one
        # event).  /queue has different semantics: each invocation must
        # produce its own full agent turn, in FIFO order, with no merging.
        # When the slot is occupied, additional /queue items land here and
        # are promoted one-at-a-time after each run's drain.  Cleared on
        # /new and /reset.  /model and other mid-session operations
        # preserve the queue.
        self._queued_events: Dict[str, List[MessageEvent]] = {}
        self._pending_native_image_paths_by_session: Dict[str, List[str]] = {}
        self._busy_ack_ts: Dict[str, float] = {}  # last busy-ack timestamp per session (debounce)
        self._session_run_generation: Dict[str, int] = {}
        # Startup restore gate: while restart-interrupted sessions are being
        # auto-resumed, real inbound messages are queued instead of competing
        # with the synthetic resume turns for the same session.  The queued
        # events drain only after all startup resume tasks have finished.
        self._startup_restore_in_progress = False
        self._startup_restore_queue: List[MessageEvent] = []
        self._startup_restore_tasks: List[asyncio.Task] = []
        # LRU cache of live SessionSources keyed by session_key. Used by
        # fallback routing paths (shutdown notifications, synthetic
        # background-process events) when the persisted origin is missing
        # and _parse_session_key can't recover thread_id. Capped so it
        # cannot grow unbounded over a long-running gateway lifetime.
        self._session_sources: "OrderedDict[str, SessionSource]" = OrderedDict()
        self._session_sources_max = 512

        # Cache AIAgent instances per session to preserve prompt caching.
        # Without this, a new AIAgent is created per message, rebuilding the
        # system prompt (including memory) every turn — breaking prefix cache
        # and costing ~10x more on providers with prompt caching (Anthropic).
        # Key: session_key, Value: (AIAgent, config_signature_str)
        #
        # OrderedDict so _enforce_agent_cache_cap() can pop the least-recently-
        # used entry (move_to_end() on cache hits, popitem(last=False) for
        # eviction).  Hard cap via _AGENT_CACHE_MAX_SIZE, idle TTL enforced
        # from _session_expiry_watcher().
        import threading as _threading
        self._agent_cache: "OrderedDict[str, tuple]" = OrderedDict()
        self._agent_cache_lock = _threading.Lock()

        # Per-session model overrides from /model command.
        # Key: session_key, Value: dict with model/provider/api_key/base_url/api_mode
        self._session_model_overrides: Dict[str, Dict[str, str]] = {}
        # Per-session reasoning effort overrides from /reasoning.
        # Key: session_key, Value: parsed reasoning config dict.
        self._session_reasoning_overrides: Dict[str, Dict[str, Any]] = {}
        self._kanban_notifier_profile = self._active_profile_name()
        # Teams meeting pipeline runtime (bound later when msgraph_webhook adapter exists).
        self._teams_pipeline_runtime = None
        self._teams_pipeline_runtime_error: Optional[str] = None
        # Track pending exec approvals per session
        # Key: session_key, Value: {"command": str, "pattern_key": str, ...}

# ===== lines 8853-8980 =====
    async def _handle_message(self, event: MessageEvent) -> Optional[str]:
        """
        Handle an incoming message from any platform.
        
        This is the core message processing pipeline:
        1. Check user authorization
        2. Check for commands (/new, /reset, etc.)
        3. Check for running agent and interrupt if needed
        4. Get or create session
        5. Build context for agent
        6. Run agent conversation
        7. Return response
        """
        source = event.source

        # 🔴 Cross-session leak guard. This handler runs inside a per-message
        # asyncio task created via create_task(), which snapshots the spawning
        # context with copy_context(). If a *concurrent* message had already
        # bound its session via set_session_vars() when this task was created,
        # we inherited ITS HERMES_SESSION_* ContextVars. Until we bind our own
        # (a few steps down, in _set_session_env), any subprocess spawned here
        # would read the foreign session's identity via the subprocess-env
        # bridge — the _UNSET-strip guard there can't help because the vars are
        # set-to-foreign, not _UNSET. Reset to _UNSET now so that window strips
        # safe (no session) instead of leaking the sibling's. See
        # gateway/session_context.reset_session_vars + the inheritance test.
        try:
            from gateway.session_context import reset_session_vars
            reset_session_vars()
        except Exception:
            logger.debug("reset_session_vars failed at handler entry", exc_info=True)

        if (
            getattr(self, "_startup_restore_in_progress", False)
            and not getattr(event, "internal", False)
            and not getattr(event, "_hermes_startup_restore_replay", False)
        ):
            self._queue_startup_restore_event(event)
            return None

        # Internal events (e.g. background-process completion notifications)
        # are system-generated and must skip user authorization.
        is_internal = bool(getattr(event, "internal", False))

        # scale-to-zero (Phase 0, 0.B/F13): stamp the gateway-scoped last-inbound
        # clock for real (user-originated) inbound only. Internal/system events
        # (background-process completions, startup-restore replays) are NOT
        # traffic — counting them would keep a genuinely idle gateway awake. This
        # clock is what the idle predicate (gateway/scale_to_zero.is_idle) reads.
        if not is_internal:
            self._scale_to_zero_note_real_inbound()

        # Fire pre_gateway_dispatch plugin hook for user-originated messages.
        # Plugins receive the MessageEvent and may return a dict influencing flow:
        #   {"action": "skip",    "reason": ...}    -> drop (no reply, plugin handled)
        #   {"action": "rewrite", "text":  ...}     -> replace event.text, continue
        #   {"action": "allow"}   /   None          -> normal dispatch
        # Hook runs BEFORE auth so plugins can handle unauthorized senders
        # (e.g. customer handover ingest) without triggering the pairing flow.
        if not is_internal:
            try:
                from hermes_cli.plugins import invoke_hook as _invoke_hook
                _hook_results = _invoke_hook(
                    "pre_gateway_dispatch",
                    event=event,
                    gateway=self,
                    session_store=self.session_store,
                )
            except Exception as _hook_exc:
                logger.warning("pre_gateway_dispatch invocation failed: %s", _hook_exc)
                _hook_results = []

            for _result in _hook_results:
                if not isinstance(_result, dict):
                    continue
                _action = _result.get("action")
                if _action == "skip":
                    logger.info(
                        "pre_gateway_dispatch skip: reason=%s platform=%s chat=%s",
                        _result.get("reason"),
                        source.platform.value if source.platform else "unknown",
                        source.chat_id or "unknown",
                    )
                    return None
                if _action == "rewrite":
                    _new_text = _result.get("text")
                    if isinstance(_new_text, str):
                        event = dataclasses.replace(event, text=_new_text)
                        source = event.source
                    break
                if _action == "allow":
                    break

        if is_internal:
            pass
        elif source.user_id is None:
            # Messages with no user identity (Telegram service messages,
            # channel forwards, anonymous admin posts, sender_chat) can't
            # be paired, but they can still be authorized via a
            # chat-scoped allowlist (e.g. TELEGRAM_GROUP_ALLOWED_CHATS
            # authorizes every member of the listed chat regardless of
            # sender). Defer to _is_user_authorized so that path runs.
            if not self._is_user_authorized(source):
                logger.debug("Ignoring message with no user_id from %s", source.platform.value)
                return None
        elif not self._is_user_authorized(source):
            logger.warning("Unauthorized user: %s (%s) on %s", source.user_id, source.user_name, source.platform.value)
            # In DMs: offer pairing code. In groups: silently ignore.
            if (
                source.chat_type == "dm"
                and self._get_unauthorized_dm_behavior(
                    source.platform,
                    profile=source.profile,
                )
                == "pair"
            ):
                platform_name = source.platform.value if source.platform else "unknown"
                # Rate-limit ALL pairing responses (code or rejection) to
                # prevent spamming the user with repeated messages when
                # multiple DMs arrive in quick succession.
                if self.pairing_store._is_rate_limited(platform_name, source.user_id):
                    return None
                code = self.pairing_store.generate_code(
                    platform_name, source.user_id, source.user_name or ""
                )
                if code:
                    adapter = self._adapter_for_source(source)
                    if adapter:

# ===== lines 10773-10850 =====
    async def _handle_message_with_agent(self, event, source, _quick_key: str, run_generation: int):
        """Inner handler that runs under the _running_agents sentinel guard."""
        _msg_start_time = time.time()
        _platform_name = source.platform.value if hasattr(source.platform, "value") else str(source.platform)
        _msg_preview = (event.text or "")[:80].replace("\n", " ")
        _reply_id = getattr(event, "reply_to_message_id", None)
        _reply_txt = (getattr(event, "reply_to_text", None) or "")[:80].replace("\n", " ")
        logger.info(
            "inbound message: platform=%s user=%s chat=%s msg=%r reply_to_id=%s reply_to_text=%r",
            _platform_name, source.user_name or source.user_id or "unknown",
            source.chat_id or "unknown", _msg_preview, _reply_id, _reply_txt,
        )

        # Get or create session
        # Topic-mode DMs: rewrite a stale/foreign thread_id to the user's
        # last-active topic so a cross-topic Reply or stripped plain reply
        # doesn't fragment the conversation across sessions.
        recovered = await asyncio.to_thread(self._recover_telegram_topic_thread_id, source)
        if recovered is not None:
            logger.info(
                "telegram topic recovery: chat=%s user=%s %r -> %s",
                source.chat_id, source.user_id, source.thread_id, recovered,
            )
            source = dataclasses.replace(source, thread_id=recovered)
            try:
                event.source = source
            except Exception:
                pass

        session_entry = await self.async_session_store.get_or_create_session(source)
        session_key = session_entry.session_key
        pinned_session_id = str(
            (getattr(event, "metadata", None) or {}).get("gateway_session_id") or ""
        ).strip()
        if pinned_session_id and pinned_session_id != session_entry.session_id:
            # Fail closed (#55578): the spawning session may have ENDED since
            # dispatch (user /new-reset, compression rotation whose parent was
            # closed). switch_session() re-opens ended sessions, so pinning
            # blindly would RESURRECT a conversation the user explicitly
            # ended and inject into it — the same illicit-revival class as
            # the ws_orphan_reap loop (#60609). A completion whose spawning
            # session is dead is dropped from injection; the subagent's
            # output remains in the delegation records.
            pinned_row = None
            try:
                if self._session_db is not None:
                    # AsyncSessionDB already offloads to a thread.
                    pinned_row = await self._session_db.get_session(pinned_session_id)
            except Exception:
                pinned_row = None
            if pinned_row is None or pinned_row.get("ended_at"):
                logger.warning(
                    "Async-delegation completion pinned to session %s, which is "
                    "%s — dropping injection instead of resurrecting it "
                    "(#55578 fail-closed; result remains in the delegation "
                    "records).",
                    pinned_session_id,
                    "unknown" if pinned_row is None else "ended",
                )
                return
            prior_session_id = session_entry.session_id
            switched = await self.async_session_store.switch_session(session_key, pinned_session_id)
            if switched is not None:
                session_entry = switched
                logger.info(
                    "Pinned async-delegation completion to spawning session %s "
                    "(was %s) for routing key %s (#57498)",
                    pinned_session_id,
                    prior_session_id,
                    session_key,
                )
        self._cache_session_source(session_key, source)
        if await asyncio.to_thread(self._is_telegram_topic_lane, source):
            try:
                binding = (await self._session_db.get_telegram_topic_binding(
                    chat_id=str(source.chat_id),
                    thread_id=str(source.thread_id),
                )) if self._session_db else None

# ===== lines 20324-20410 =====
def _start_cron_ticker(stop_event: threading.Event, adapters=None, loop=None, interval: int = 60):
    """DEPRECATED shim — preserved for backward compatibility.

    The cron trigger now lives behind the ``CronScheduler`` provider
    (``cron.scheduler_provider``); the gateway resolves a provider and runs its
    ``start()`` directly (see ``start_gateway``). This shim runs ONLY the
    built-in in-process tick loop, exactly as before, for any external caller
    or test that still references this symbol (e.g. hermes_cli/debug.py). It no
    longer runs gateway housekeeping — that moved to
    ``_start_gateway_housekeeping``.
    """
    from cron.scheduler_provider import InProcessCronScheduler
    InProcessCronScheduler().start(stop_event, adapters=adapters, loop=loop, interval=interval)


# Upper bound for cooperatively draining the cron ticker on shutdown. The cron
# thread delivers via ``safe_schedule_threadsafe`` and blocks on
# ``future.result(timeout=60)`` (see cron/scheduler.py::_deliver_result), so a
# single in-flight delivery unblocks within ~60s. The extra margin covers the
# hop back through run_one_job's bookkeeping.
_CRON_SHUTDOWN_DRAIN_TIMEOUT = 65.0

# Upper bound for cooperatively draining the housekeeping ticker on shutdown.
# Housekeeping periodically refreshes the channel directory via
# ``safe_schedule_threadsafe(build_channel_directory(...), loop)`` and blocks on
# ``fut.result(timeout=30)`` (see ``_start_gateway_housekeeping``) — the same
# loop-scheduled-future pattern as cron. So the cooperative bound must cover
# that 30s future (plus margin) rather than the old 5s join, otherwise a
# channel-directory refresh in flight at shutdown gets abandoned mid-resolve.
# Unlike a dropped cron delivery this is not user-facing (it self-heals on the
# next tick), but bounding it correctly keeps the drain honest.
_HOUSEKEEPING_SHUTDOWN_DRAIN_TIMEOUT = 35.0


async def _await_thread_exit(
    thread: Optional[threading.Thread], timeout: float, poll: float = 0.1
) -> bool:
    """Wait for a daemon thread to exit WITHOUT blocking the event loop.

    A synchronous ``thread.join()`` here would freeze the event loop — fatal
    for the cron ticker, whose in-flight delivery is a coroutine scheduled onto
    *this* loop via ``safe_schedule_threadsafe``. Blocking the loop deadlocks
    that delivery (the loop can never run it), so ``join(timeout=5)`` always
    times out and the message is silently dropped on restart (#58818).

    Polling ``is_alive()`` with ``await asyncio.sleep`` keeps the loop running
    so the pending delivery completes, then the ticker sees ``stop_event`` and
    exits. Returns True if the thread exited within ``timeout``.
    """
    if thread is None:
        return True
    deadline = asyncio.get_running_loop().time() + max(0.0, timeout)
    while thread.is_alive() and asyncio.get_running_loop().time() < deadline:
        await asyncio.sleep(poll)
    return not thread.is_alive()


async def start_gateway(config: Optional[GatewayConfig] = None, replace: bool = False, verbosity: Optional[int] = 0) -> bool:
    """
    Start the gateway and run until interrupted.
    
    This is the main entry point for running the gateway.
    Returns True if the gateway ran successfully, False if it failed to start.
    A False return causes a non-zero exit code so systemd can auto-restart.
    
    Args:
        config: Optional gateway configuration override.
        replace: If True, kill any existing gateway instance before starting.
                 Useful for systemd services to avoid restart-loop deadlocks
                 when the previous process hasn't fully exited yet.
    """
    # Snapshot the checkout revision now, while sys.modules still matches disk,
    # so a later `git pull` under this long-lived process can be detected (and
    # risky work like model switching refused) instead of crashing on a stale
    # in-memory module.
    from gateway.code_skew import record_boot_fingerprint
    record_boot_fingerprint()

    # ── Duplicate-instance guard ──────────────────────────────────────
    # Prevent two gateways from running under the same HERMES_HOME.
    # The PID file is scoped to HERMES_HOME, so future multi-profile
    # setups (each profile using a distinct HERMES_HOME) will naturally
    # allow concurrent instances without tripping this guard.
    from gateway.status import (
        acquire_gateway_runtime_lock,
        get_running_pid,
        get_process_start_time,

# ===== lines 20816-20890 =====
        # running mode; preserve that lifecycle path without starting cron.
        await runner.wait_for_shutdown()
        if runner.should_exit_with_failure:
            if runner.exit_reason:
                logger.error("Gateway exiting with failure: %s", runner.exit_reason)
            return False
        try:
            from tools.mcp_tool import shutdown_mcp_servers
            shutdown_mcp_servers()
        except Exception:
            pass
        if runner.exit_code is not None:
            raise SystemExit(runner.exit_code)
        return True
    
    # Start the background cron scheduler via the resolved provider so
    # scheduled jobs fire automatically. The built-in provider is the
    # historical in-process 60s ticker; an external provider (e.g. chronos)
    # may arm a schedule and return. Pass the event loop so cron delivery can
    # use live adapters (E2EE support).
    from cron.scheduler_provider import resolve_cron_scheduler
    cron_stop = threading.Event()
    cron_provider = resolve_cron_scheduler()
    cron_thread = threading.Thread(
        target=cron_provider.start,
        args=(cron_stop,),
        kwargs={"adapters": runner.adapters, "loop": asyncio.get_running_loop()},
        daemon=True,
        name="cron-scheduler",
    )
    cron_thread.start()

    # Gateway-only periodic housekeeping (channel dir, cache cleanup, paste
    # sweep, curator) — runs independently of which cron provider is active.
    # Shares cron_stop as the shutdown signal.
    housekeeping_thread = threading.Thread(
        target=_start_gateway_housekeeping,
        args=(cron_stop,),
        kwargs={"adapters": runner.adapters, "loop": asyncio.get_running_loop()},
        daemon=True,
        name="gateway-housekeeping",
    )
    housekeeping_thread.start()
    
    # Wait for shutdown
    await runner.wait_for_shutdown()

    try:
        from hermes_cli.nous_auth_keepalive import stop_nous_auth_keepalive

        stop_nous_auth_keepalive()
    except Exception:
        pass

    if runner.should_exit_with_failure:
        if runner.exit_reason:
            logger.error("Gateway exiting with failure: %s", runner.exit_reason)
        return False
    
    # Stop cron scheduler + housekeeping cleanly.
    #
    # These MUST be awaited cooperatively, not join()ed. A cron delivery in
    # flight when the gateway restarts is a coroutine scheduled onto THIS event
    # loop (safe_schedule_threadsafe); the ticker thread is blocked on its
    # future.result(). A synchronous cron_thread.join() would block the loop,
    # so that delivery could never run — it timed out and the message was
    # silently dropped (#58818). Awaiting keeps the loop alive so the in-flight
    # delivery finishes before we tear down.
    cron_stop.set()
    try:
        cron_provider.stop()
    except Exception as e:
        logger.debug("Cron provider stop() error: %s", e)
    if not await _await_thread_exit(cron_thread, timeout=_CRON_SHUTDOWN_DRAIN_TIMEOUT):
        logger.warning(

