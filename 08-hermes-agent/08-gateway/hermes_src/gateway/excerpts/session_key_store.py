# Excerpt from gateway/session.py
# Session key + store

# ===== lines 148-330 =====
class SessionSource:
    """
    Describes where a message originated from.
    
    This information is used to:
    1. Route responses back to the right place
    2. Inject context into the system prompt
    3. Track origin for cron job delivery
    """
    platform: Platform
    chat_id: str
    chat_name: Optional[str] = None
    chat_type: str = "dm"  # "dm", "group", "channel", "thread"
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    thread_id: Optional[str] = None  # For forum topics, Discord threads, etc.
    chat_topic: Optional[str] = None  # Channel topic/description (Discord, Slack)
    user_id_alt: Optional[str] = None  # Platform-specific stable alt ID (Signal UUID, Feishu union_id)
    chat_id_alt: Optional[str] = None  # Signal group internal ID
    is_bot: bool = False  # True when the message author is a bot/webhook (Discord)
    # Platform-neutral SCOPE discriminator (Discord guild / Slack workspace /
    # Matrix server). Drives server/workspace isolation + the relay δ/ε/ζ gate.
    # Wire migration (D-Q2.5): `scope_id` is the canonical name; `guild_id` is a
    # deprecated legacy alias kept during the cross-repo dual-read/dual-write
    # overlap. Both are written by to_dict and read by from_dict (scope_id wins);
    # the `guild_id` alias is dropped in a follow-up once both repos deploy.
    scope_id: Optional[str] = None
    guild_id: Optional[str] = None  # @deprecated legacy alias for scope_id (D-Q2.5)
    parent_chat_id: Optional[str] = None  # Parent channel when chat_id refers to a thread
    message_id: Optional[str] = None  # ID of the triggering message (for pin/reply/react)
    role_authorized: bool = False  # True when adapter granted access via role (not user ID)
    # Profile this inbound message is routed to in a multiplexing gateway
    # (from the /p/<profile>/ URL prefix or per-credential adapter ownership).
    # None => the gateway's active/default profile. Drives both session-key
    # namespacing and the per-turn config/credential scope.
    profile: Optional[str] = None

    # Discord auto-thread metadata.  Newly auto-created Discord threads start
    # with a fast placeholder title from the raw message, then the gateway can
    # rename them after the first agent turn using the generated session title.
    # Keep this explicit so pre-existing or human-renamed threads are not
    # mistaken for safe rename targets.
    auto_thread_created: bool = False
    auto_thread_initial_name: Optional[str] = None

    # Internal, wire-INVISIBLE trust signal: True when this event was delivered
    # to the gateway over the per-instance-authenticated relay WebSocket (the
    # Team Gateway connector). The connector authenticates the gateway's socket
    # with a per-instance secret and resolves owner-only author bindings BEFORE
    # delivering, so a relay-delivered event is already authorized as this
    # instance's bound user. ``platform`` carries the UNDERLYING platform
    # (e.g. ``discord``) for session-keying/egress, NOT ``relay`` — so authz
    # must key the upstream-trust decision off THIS flag, not off ``platform``.
    # Set locally by the relay transport (``ws_transport._event_from_wire``);
    # deliberately excluded from ``to_dict``/``from_dict`` so a peer can never
    # forge it across the wire or have it restored from persistence.
    delivered_via_upstream_relay: bool = False

    def __post_init__(self) -> None:
        # D-Q2.5 dual-field reconciliation: `scope_id` is canonical, `guild_id`
        # is the deprecated alias. Mirror whichever was provided onto the other
        # (scope_id wins on conflict) so internal readers of EITHER field see the
        # same value during the cross-repo wire migration overlap.
        if self.scope_id is None and self.guild_id is not None:
            self.scope_id = self.guild_id
        elif self.scope_id is not None:
            self.guild_id = self.scope_id

    @property
    def description(self) -> str:
        """Human-readable description of the source."""
        if self.platform == Platform.LOCAL:
            return "CLI terminal"
        
        parts = []
        if self.chat_type == "dm":
            parts.append(f"DM with {self.user_name or self.user_id or 'user'}")
        elif self.chat_type == "group":
            parts.append(f"group: {self.chat_name or self.chat_id}")
        elif self.chat_type == "channel":
            parts.append(f"channel: {self.chat_name or self.chat_id}")
        else:
            parts.append(self.chat_name or self.chat_id)
        
        if self.thread_id:
            parts.append(f"thread: {self.thread_id}")
        
        return ", ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        d = {
            "platform": self.platform.value,
            "chat_id": self.chat_id,
            "chat_name": self.chat_name,
            "chat_type": self.chat_type,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "thread_id": self.thread_id,
            "chat_topic": self.chat_topic,
        }
        if self.user_id_alt:
            d["user_id_alt"] = self.user_id_alt
        if self.chat_id_alt:
            d["chat_id_alt"] = self.chat_id_alt
        # D-Q2.5 dual-write: emit BOTH the canonical `scope_id` and the
        # deprecated `guild_id` alias (mirrored in __post_init__) so a connector
        # on either side of the migration resolves the scope. Drop `guild_id`
        # in the follow-up once both repos are on `scope_id`.
        scope = self.scope_id if self.scope_id is not None else self.guild_id
        if scope:
            d["scope_id"] = scope
            d["guild_id"] = scope
        if self.parent_chat_id:
            d["parent_chat_id"] = self.parent_chat_id
        if self.message_id:
            d["message_id"] = self.message_id
        if self.profile:
            d["profile"] = self.profile
        if self.auto_thread_created:
            d["auto_thread_created"] = True
        if self.auto_thread_initial_name:
            d["auto_thread_initial_name"] = self.auto_thread_initial_name
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionSource":
        return cls(
            platform=Platform(data["platform"]),
            chat_id=str(data["chat_id"]),
            chat_name=data.get("chat_name"),
            chat_type=data.get("chat_type", "dm"),
            user_id=data.get("user_id"),
            user_name=data.get("user_name"),
            thread_id=data.get("thread_id"),
            chat_topic=data.get("chat_topic"),
            user_id_alt=data.get("user_id_alt"),
            chat_id_alt=data.get("chat_id_alt"),
            # D-Q2.5 dual-read: prefer the canonical `scope_id`, fall back to the
            # deprecated `guild_id` alias (a peer not yet migrated still sends it).
            scope_id=data.get("scope_id", data.get("guild_id")),
            parent_chat_id=data.get("parent_chat_id"),
            message_id=data.get("message_id"),
            profile=data.get("profile"),
            auto_thread_created=bool(data.get("auto_thread_created", False)),
            auto_thread_initial_name=data.get("auto_thread_initial_name"),
        )
    


@dataclass
class SessionContext:
    """
    Full context for a session, used for dynamic system prompt injection.
    
    The agent receives this information to understand:
    - Where messages are coming from
    - What platforms are available
    - Where it can deliver scheduled task outputs
    """
    source: SessionSource
    connected_platforms: List[Platform]
    home_channels: Dict[Platform, HomeChannel]
    shared_multi_user_session: bool = False
    
    # Session metadata
    session_key: str = ""
    session_id: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source.to_dict(),
            "connected_platforms": [p.value for p in self.connected_platforms],
            "home_channels": {
                p.value: hc.to_dict() for p, hc in self.home_channels.items()
            },
            "shared_multi_user_session": self.shared_multi_user_session,
            "session_key": self.session_key,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# ===== lines 871-960 =====
def build_session_key(
    source: SessionSource,
    group_sessions_per_user: bool = True,
    thread_sessions_per_user: bool = False,
    profile: Optional[str] = None,
) -> str:
    """Build a deterministic session key from a message source.

    This is the single source of truth for session key construction.

    ``profile`` selects the key namespace (see :func:`_session_key_namespace`).
    It defaults to ``None`` ⇒ the legacy ``agent:main`` namespace, so callers
    that don't multiplex produce byte-identical keys to before. Only the
    multiplexing gateway passes a non-default profile.

    DM rules:
      - DMs include chat_id when present, so each private conversation is isolated.
      - thread_id further differentiates threaded DMs within the same DM chat.
      - Without chat_id, thread_id is used as a best-effort fallback.
      - Without thread_id or chat_id, DMs share a single session.

    Group/channel rules:
      - chat_id identifies the parent group/channel.
      - user_id/user_id_alt isolates participants within that parent chat when available when
        ``group_sessions_per_user`` is enabled.
      - thread_id differentiates threads within that parent chat.  When
        ``thread_sessions_per_user`` is False (default), threads are *shared* across all
        participants — user_id is NOT appended, so every user in the thread
        shares a single session.  This is the expected UX for threaded
        conversations (Telegram forum topics, Discord threads, Slack threads).
      - Without participant identifiers, or when isolation is disabled, messages fall back to one
        shared session per chat.
      - Without identifiers, messages fall back to one session per platform/chat_type.
    """
    ns = _session_key_namespace(profile)
    platform = source.platform.value
    if source.chat_type == "dm":
        dm_chat_id = source.chat_id
        if source.platform == Platform.WHATSAPP:
            dm_chat_id = canonical_whatsapp_identifier(source.chat_id)

        if dm_chat_id:
            if source.thread_id:
                return f"{ns}:{platform}:dm:{dm_chat_id}:{source.thread_id}"
            return f"{ns}:{platform}:dm:{dm_chat_id}"
        # No chat_id — fall back to the sender's own identifier before the
        # bare per-platform sink.  Without this, every DM from every user that
        # arrives without a chat_id (non-standard adapters / synthetic sources)
        # collapses into one shared "<ns>:<platform>:dm" session, and a
        # single cached agent ends up serving multiple people's conversations —
        # cross-user history bleed.  participant_id keeps DMs isolated per user.
        dm_participant_id = source.user_id_alt or source.user_id
        if dm_participant_id and source.platform == Platform.WHATSAPP:
            dm_participant_id = (
                canonical_whatsapp_identifier(str(dm_participant_id))
                or dm_participant_id
            )
        if dm_participant_id:
            if source.thread_id:
                return f"{ns}:{platform}:dm:{dm_participant_id}:{source.thread_id}"
            return f"{ns}:{platform}:dm:{dm_participant_id}"
        if source.thread_id:
            return f"{ns}:{platform}:dm:{source.thread_id}"
        return f"{ns}:{platform}:dm"

    participant_id = source.user_id_alt or source.user_id
    if participant_id and source.platform == Platform.WHATSAPP:
        # Same JID/LID-flip bug as the DM case: without canonicalisation, a
        # single group member gets two isolated per-user sessions when the
        # bridge reshuffles alias forms.
        participant_id = canonical_whatsapp_identifier(str(participant_id)) or participant_id
    key_parts = [ns, platform, source.chat_type]

    if source.chat_id:
        key_parts.append(source.chat_id)
    if source.thread_id:
        key_parts.append(source.thread_id)

    # In threads, default to shared sessions (all participants see the same
    # conversation).  Per-user isolation only applies when explicitly enabled
    # via thread_sessions_per_user, or when there is no thread (regular group).
    isolate_user = group_sessions_per_user
    if source.thread_id and not thread_sessions_per_user:
        isolate_user = False

    if isolate_user and participant_id:
        key_parts.append(str(participant_id))

    return ":".join(key_parts)


# ===== lines 1775-1860 =====
    def get_or_create_session(
        self,
        source: SessionSource,
        force_new: bool = False,
    ) -> SessionEntry:
        """Single-flight session lookup/create per routing key.

        Calls for different keys remain concurrent. Overlapping calls for the
        same key share the owner's result, including concurrent ``force_new``
        deliveries, so only one routing transition and SQLite row is created.
        """
        session_key = self._generate_session_key(source)
        inflight_lock = getattr(self, "_inflight_lock", None)
        if inflight_lock is None:
            inflight_lock = threading.Lock()
            self._inflight_lock = inflight_lock
            self._inflight_sessions = {}

        with inflight_lock:
            slot = self._inflight_sessions.get(session_key)
            if slot is None:
                slot = _SessionFlight()
                self._inflight_sessions[session_key] = slot
                owner = True
            else:
                owner = False

        if not owner:
            slot.event.wait()
            if slot.error is not None:
                raise slot.error
            assert slot.result is not None
            return slot.result

        try:
            result = self._get_or_create_session_impl(source, force_new=force_new)
            slot.result = result
            return result
        except BaseException as exc:
            slot.error = exc
            raise
        finally:
            slot.event.set()
            with inflight_lock:
                self._inflight_sessions.pop(session_key, None)

    def _get_or_create_session_impl(
        self,
        source: SessionSource,
        force_new: bool = False,
    ) -> SessionEntry:
        """Perform one session routing transition for the single-flight owner.

        All blocking I/O (SQLite SELECTs, routing-index rewrite + ``os.fsync``,
        recovery DB queries) is performed *outside* ``self._lock``. The lock
        protects only ``_entries`` / ``_loaded`` mutations.
        """
        session_key = self._generate_session_key(source)
        now = _now()

        db_end_session_id = None
        db_create_kwargs = None
        existing_session_id = None
        force_new_observed_entry = None

        # ---- Phase 0: lock read -- existing session_id for compression tip ----
        if not force_new:
            with self._lock:
                self._ensure_loaded_locked()
                entry = self._entries.get(session_key)
                if entry is not None:
                    existing_session_id = entry.session_id

        # Compression tip lookup outside the lock (DB I/O).
        canonical_existing_session_id = (
            self._compression_tip_for_session_id(existing_session_id)
            if existing_session_id
            else None
        )

        # ---- Phase 1: lock read -- get entry snapshot for stale/reset checks ----
        _stale_session_id = None
        _entry_for_checks = None
        with self._lock:
            self._ensure_loaded_locked()
            if force_new:

