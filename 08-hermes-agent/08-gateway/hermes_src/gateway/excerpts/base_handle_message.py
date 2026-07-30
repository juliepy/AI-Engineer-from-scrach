# Excerpt from gateway/platforms/base.py
# Adapter message entry + active-session guard

# ===== lines 2253-2360 =====
class BasePlatformAdapter(ABC):
    """
    Base class for platform adapters.
    
    Subclasses implement platform-specific logic for:
    - Connecting and authenticating
    - Receiving messages
    - Sending messages/responses
    - Handling media
    """

    # Whether this platform renders triple-backtick fenced code blocks (i.e.
    # ``format_message`` translates/preserves markdown fences into a real code
    # block).  Capability flag for markdown-aware presentation choices.
    # Default False (plain-text platforms); markdown-rendering adapters set True.
    # Tool-progress uses this to render a terminal command as a bare fenced code
    # block (no language tag — Slack mrkdwn would print the tag as a literal
    # first code line).  Plain-text platforms fall back to the short truncated
    # preview (see gateway/run.py progress_callback).
    supports_code_blocks: bool = False

    # Whether this adapter can deliver an ASYNC notification back to the agent
    # AFTER a turn ends — i.e. wake a fresh turn to surface a background
    # process completion (terminal notify_on_complete / watch_patterns) or a
    # detached subagent result (delegate_task background=True).
    #
    # True for adapters that hold a persistent outbound channel (Telegram,
    # Discord, Slack, ... — they have a real ``send()`` and the gateway runs
    # the watcher/drain loops). False for stateless request/response adapters
    # (the API server): every route closes its channel when the turn ends, so
    # there is nowhere to push a later completion. The gateway propagates this
    # into the ``HERMES_SESSION_ASYNC_DELIVERY`` contextvar at session-bind
    # time; tools read it via ``async_delivery_supported()`` and refuse to make
    # a delivery promise they can't keep. A new stateless adapter only needs to
    # set this to False to stay correct-by-default.
    supports_async_delivery: bool = True

    # Whether this adapter's ``send()`` splits long content into multiple
    # messages via ``truncate_message()``.  When True, the delivery router
    # (gateway/delivery.py) skips gateway-level truncation and lets the
    # adapter chunk natively — preserving full output on platforms that
    # support multi-message delivery (Discord, Telegram, …).  Default False
    # (conservative); adapters verified to chunk in ``send()`` set True.
    splits_long_messages: bool = False

    # The command prefix users can always TYPE on this platform to reach
    # Hermes commands.  Default "/" (most platforms deliver "/approve" etc.
    # as plain message text).  Platforms where typing a leading "/" is
    # intercepted or restricted by the client (Slack blocks native slash
    # commands inside threads; Matrix clients reserve "/" for client-local
    # commands) ship a "!" alias rewrite in their adapter and set this to
    # "!" so user-facing instruction text ("Reply `!approve` ...") tells
    # users the form that actually works everywhere.  Capability flag —
    # shared prompt builders read it via getattr(adapter,
    # "typed_command_prefix", "/"); no per-platform branching at call sites.
    typed_command_prefix: str = "/"

    # Whether this adapter supports the ``in_channel`` continuable-cron surface
    # (``platforms.<p>.extra.cron_continuable_surface: in_channel``): a
    # continuable cron job delivered FLAT into a channel (no dedicated thread),
    # with the user's plain channel reply continuing the job in-context via the
    # shared-channel session.  Only coherent on a platform that has BOTH a
    # flat-reply outbound gate AND a whole-channel inbound session bucket keyed
    # ``(platform, chat_id, None)`` — today that is Slack (``reply_in_thread:
    # false``).  Default False: an unsupported platform fails SAFE, treating
    # ``in_channel`` as ``thread`` (a threaded continuation ≈ today's
    # behaviour), never a dropped continuation.  Read generically by the cron
    # scheduler via ``getattr(adapter, "supports_inchannel_continuable",
    # False)`` — no per-platform branching at the call site (the key stays a
    # generic seam; Slack is merely the first consumer).
    supports_inchannel_continuable: bool = False

    def __init__(self, config: PlatformConfig, platform: Platform):
        self.config = config
        self.platform = platform
        self._message_handler: Optional[MessageHandler] = None
        # Optional hook (e.g. Telegram DM topic recovery) that rewrites
        # ``event.source.thread_id`` before session keying. Returns the
        # corrected thread_id or None to leave the source untouched.
        self._topic_recovery_fn: Optional[Callable[[Any], Optional[str]]] = None
        self._running = False
        self._fatal_error_code: Optional[str] = None
        self._fatal_error_message: Optional[str] = None
        self._fatal_error_retryable = True
        self._fatal_error_handler: Optional[Callable[["BasePlatformAdapter"], Awaitable[None] | None]] = None
        
        # Track active message handlers per session for interrupt support.
        # _active_sessions stores the per-session interrupt Event; _session_tasks
        # maps session → the specific Task currently processing it so that
        # session-terminating commands (/stop, /new, /reset) can cancel the
        # right task and release the adapter-level guard deterministically.
        # Without the owner-task map, an old task's finally block could delete
        # a newer task's guard, leaving stale busy state.
        self._active_sessions: Dict[str, asyncio.Event] = {}
        self._pending_messages: Dict[str, MessageEvent] = {}
        self._session_tasks: Dict[str, asyncio.Task] = {}
        # Legacy busy_text_mode env var; when unset the runner syncs the
        # resolved value (driven by busy_input_mode) onto the adapter after
        # construction (gateway/run.py). Default to "interrupt" so a stray
        # pre-sync read matches the single-knob default rather than silently
        # queueing.
        self._busy_text_mode: str = (
            os.environ.get("HERMES_GATEWAY_BUSY_TEXT_MODE", "interrupt").strip().lower()
            or "interrupt"
        )
        self._busy_text_debounce_seconds: float = _float_env(
            "HERMES_GATEWAY_BUSY_TEXT_DEBOUNCE_SECONDS", 0.35
        )

# ===== lines 4585-4780 =====
    async def handle_message(self, event: MessageEvent) -> None:
        """
        Process an incoming message.
        
        This method returns quickly by spawning background tasks.
        This allows new messages to be processed even while an agent is running,
        enabling interruption support.
        """
        if not self._message_handler:
            return

        coerce_plaintext_gateway_command(event)

        # Rewrite ``event.source.thread_id`` via the installed recovery hook
        # (Telegram DM topic mode) so the session key, guard checks, and
        # downstream delivery all agree on the same lane.
        # Offloaded: the sync hook must not block the loop.
        await asyncio.to_thread(self._apply_topic_recovery, event)

        session_key = build_session_key(
            event.source,
            group_sessions_per_user=self.config.extra.get("group_sessions_per_user", True),
            thread_sessions_per_user=self.config.extra.get("thread_sessions_per_user", False),
        )

        # On-entry self-heal: if the adapter still has an _active_sessions
        # entry for this key but the owner task has already exited (done or
        # cancelled), the lock is stale.  Clear it and fall through to
        # normal dispatch so the user isn't trapped behind a dead guard —
        # this is the split-brain tail described in issue #11016.
        if session_key in self._active_sessions:
            self._heal_stale_session_lock(session_key)

        # Check if there's already an active handler for this session
        if session_key in self._active_sessions:
            # Certain commands must bypass the active-session guard and be
            # dispatched directly to the gateway runner.  Without this, they
            # are queued as pending messages and either:
            #   - leak into the conversation as user text (/stop, /new), or
            #   - deadlock (/approve, /deny — agent is blocked on Event.wait)
            #
            # Dispatch inline: call the message handler directly and send the
            # response.  Do NOT use _process_message_background — it manages
            # session lifecycle and its cleanup races with the running task
            # (see PR #4926).
            cmd = event.get_command()
            from hermes_cli.commands import should_bypass_active_session

            if should_bypass_active_session(cmd):
                # /stop, /new, /reset must cancel the in-flight adapter task
                # and preserve ordering of queued follow-ups.  Route those
                # through the dedicated handoff path that serializes
                # cancellation + runner response + pending drain.
                if cmd in {"stop", "new", "reset"}:
                    self._discard_text_debounce(session_key)
                    try:
                        await self._dispatch_active_session_command(event, session_key, cmd)
                    except Exception as e:
                        logger.error(
                            "[%s] Command '/%s' dispatch failed: %s",
                            self.name, cmd, e, exc_info=True,
                        )
                    return

                # Other bypass commands (/approve, /deny, /status,
                # /background, /restart) just need direct dispatch — they
                # don't cancel the running task.
                logger.debug(
                    "[%s] Command '/%s' bypassing active-session guard for %s",
                    self.name, cmd, session_key,
                )
                try:
                    _thread_meta = _thread_metadata_for_source(event.source, _reply_anchor_for_event(event))
                    response = await self._message_handler(event)
                    _text, _eph_ttl = self._unwrap_ephemeral(response)
                    if _text:
                        _r = await self._send_with_retry(
                            chat_id=event.source.chat_id,
                            content=_text,
                            reply_to=_reply_anchor_for_event(event),
                            metadata=_mark_notify_metadata(_thread_meta),
                        )
                        if _eph_ttl > 0 and _r.success and _r.message_id:
                            self._schedule_ephemeral_delete(
                                chat_id=event.source.chat_id,
                                message_id=_r.message_id,
                                ttl_seconds=_eph_ttl,
                            )
                except Exception as e:
                    logger.error("[%s] Command '/%s' dispatch failed: %s", self.name, cmd, e, exc_info=True)
                return

            # Clarify reply bypass: if the agent is blocked on a
            # clarify_tool call, the next non-command message in this
            # session MUST reach the runner so typed numeric choices,
            # exact choices, and free-form "Other" answers can resolve the
            # clarify-intercept and unblock the agent.
            #
            # Without this bypass: the message gets queued in
            # _pending_messages as a follow-up turn instead of reaching the
            # clarify resolver, leaving the agent blocked and discarding the
            # user's answer.
            # Same shape as the /approve deadlock fix (PR #4926) — both
            # cases are "agent thread blocked on Event.wait, message must
            # reach the resolver before being treated as a new turn."
            if not cmd:
                try:
                    from tools import clarify_gateway as _clarify_mod
                    _has_text_clarify = (
                        _clarify_mod.get_pending_for_session(
                            session_key,
                            include_choice_prompts=True,
                        ) is not None
                    )
                except Exception:
                    _has_text_clarify = False

                if _has_text_clarify:
                    logger.debug(
                        "[%s] Routing message to clarify text-intercept for %s",
                        self.name, session_key,
                    )
                    try:
                        _thread_meta = _thread_metadata_for_source(
                            event.source, _reply_anchor_for_event(event)
                        )
                        response = await self._message_handler(event)
                        _text, _eph_ttl = self._unwrap_ephemeral(response)
                        if _text:
                            _r = await self._send_with_retry(
                                chat_id=event.source.chat_id,
                                content=_text,
                                reply_to=_reply_anchor_for_event(event),
                                metadata=_mark_notify_metadata(_thread_meta),
                            )
                            if _eph_ttl > 0 and _r.success and _r.message_id:
                                self._schedule_ephemeral_delete(
                                    chat_id=event.source.chat_id,
                                    message_id=_r.message_id,
                                    ttl_seconds=_eph_ttl,
                                )
                    except Exception as e:
                        logger.error(
                            "[%s] Clarify text-intercept dispatch failed: %s",
                            self.name, e, exc_info=True,
                        )
                    return

            if self._busy_session_handler is not None:
                try:
                    if await self._busy_session_handler(event, session_key):
                        return
                except Exception as e:
                    logger.error("[%s] Busy-session handler failed: %s", self.name, e, exc_info=True)

            # Special case: photo bursts/albums frequently arrive as multiple near-
            # simultaneous messages. Queue them without interrupting the active run,
            # then process them immediately after the current task finishes.
            if event.message_type == MessageType.PHOTO:
                logger.debug("[%s] Queuing photo follow-up for session %s without interrupt", self.name, session_key)
                merge_pending_message_event(self._pending_messages, session_key, event)
                return  # Don't interrupt now - will run after current task completes

            if self._is_queue_text_debounce_candidate(event):
                logger.debug(
                    "[%s] New text message while session %s is active — "
                    "debouncing follow-up (busy_text_mode=queue, window=%.2fs)",
                    self.name,
                    session_key,
                    self._busy_text_debounce_seconds,
                )
                await self._queue_text_debounce(session_key, event)
            else:
                logger.debug(
                    "[%s] New message while session %s is active — queuing follow-up "
                    "(no interrupt, will cascade after current turn)",
                    self.name,
                    session_key,
                )
                merge_pending_message_event(
                    self._pending_messages,
                    session_key,
                    event,
                    merge_text=event.message_type == MessageType.TEXT,
                )
            return  # Don't process now - will be handled after current task finishes
        
        # Mark session as active BEFORE spawning background task to close
        # the race window where a second message arriving before the task
        # starts would also pass the _active_sessions check and spawn a
        # duplicate task.  (grammY sequentialize / aiogram EventIsolation
        # pattern — set the guard synchronously, not inside the task.)
        # _start_session_processing installs the guard AND the owner-task
        # mapping atomically so stale-lock detection works.
        self._start_session_processing(event, session_key)
    

# ===== lines 4808-4920 =====
    async def _process_message_background(self, event: MessageEvent, session_key: str) -> None:
        """Background task that actually processes the message."""
        # Track delivery outcomes for the processing-complete hook
        delivery_attempted = False
        delivery_succeeded = False

        def _record_delivery(result):
            nonlocal delivery_attempted, delivery_succeeded
            if result is None:
                return
            delivery_attempted = True
            if getattr(result, "success", False):
                delivery_succeeded = True

        # Reuse the interrupt event set by handle_message() (which marks
        # the session active before spawning this task to prevent races).
        # Fall back to a new Event only if the entry was removed externally.
        interrupt_event = self._active_sessions.get(session_key) or asyncio.Event()
        self._active_sessions[session_key] = interrupt_event
        
        # Start continuous typing indicator (refreshes every 2 seconds).
        # Gated per-platform: when typing_indicator=False the refresh loop is
        # never spawned, so no "typing…" / "is thinking…" status is shown.
        # typing_task stays None; _stop_typing_refresh already no-ops on None.
        _thread_metadata = _thread_metadata_for_source(event.source, _reply_anchor_for_event(event))
        typing_task: Optional[asyncio.Task] = None
        if getattr(self.config, "typing_indicator", True):
            _keep_typing_kwargs: Dict[str, Any] = {"metadata": _thread_metadata}
            try:
                _keep_typing_sig = inspect.signature(self._keep_typing)
            except (TypeError, ValueError):
                _keep_typing_sig = None
            if _keep_typing_sig is None or "stop_event" in _keep_typing_sig.parameters:
                _keep_typing_kwargs["stop_event"] = interrupt_event
            typing_task = asyncio.create_task(
                self._keep_typing(
                    event.source.chat_id,
                    **_keep_typing_kwargs,
                )
            )

        async def _stop_typing_task() -> None:
            await self._stop_typing_refresh(
                event.source.chat_id,
                typing_task,
            )
        
        try:
            await self._run_processing_hook("on_processing_start", event)

            # Call the handler (this can take a while with tool calls)
            response = await self._message_handler(event)
            is_ephemeral_response = isinstance(response, EphemeralReply)

            # Slash-command handlers may return an EphemeralReply sentinel to
            # request that their reply message auto-delete after a TTL (used
            # for system notices like "✨ New session started!" that the user
            # doesn't need to keep in the thread).  Unwrap here so all the
            # downstream extract_media / text-processing logic sees a plain
            # string, and remember the TTL + platform capability so the
            # post-send block can schedule the deletion.
            response, _ephemeral_ttl = self._unwrap_ephemeral(response)

            # Send response if any.  A None/empty response is normal when
            # streaming already delivered the text (already_sent=True) or
            # when the message was queued behind an active agent.  Log at
            # DEBUG to avoid noisy warnings for expected behavior.
            #
            # Suppress stale response when the session was interrupted by a
            # new message that hasn't been consumed yet.  The pending message
            # is processed by the pending-message handler below (#8221/#2483).
            if (
                response
                and interrupt_event.is_set()
                and session_key in self._pending_messages
            ):
                logger.info(
                    "[%s] Suppressing stale response for interrupted session %s",
                    self.name,
                    session_key,
                )
                response = None
            if not response:
                logger.debug("[%s] Handler returned empty/None response for %s", self.name, event.source.chat_id)
            if response:
                # Capture [[as_document]] before extract_media strips it, so the
                # dispatch partition below can route image-extension files
                # through send_document instead of send_multiple_images. Used
                # by skills that produce large/lossless images (e.g. info-graph)
                # where Telegram's sendPhoto recompression destroys legibility.
                force_document_attachments = "[[as_document]]" in response

                # Pre-extract snapshot for the #29346 recovery/invariant below.
                _response_pre_extract = response

                # Extract MEDIA:<path> tags (from TTS tool) before other processing
                media_files, response = self.extract_media(response)
                media_files = self.filter_media_delivery_paths(media_files)

                # Extract image URLs and send them as native platform attachments
                images, text_content = self.extract_images(response)
                # Strip any remaining internal directives from message body (fixes #1561).
                # _strip_media_directives shares MEDIA_TAG_CLEANUP_RE, so a MEDIA: tag
                # with an unknown extension is intentionally left in the body for
                # extract_local_files below to pick up rather than silently dropped (#34517).
                text_content = _strip_media_directives(text_content).strip()
                if images:
                    logger.info("[%s] extract_images found %d image(s) in response (%d chars)", self.name, len(images), len(response))

                local_files = []
                if not is_ephemeral_response:
                    # Auto-detect bare local file paths for native media delivery
                    # (helps small models that don't use MEDIA: syntax). Skip

