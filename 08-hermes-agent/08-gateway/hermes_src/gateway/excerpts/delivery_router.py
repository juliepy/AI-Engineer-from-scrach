# Excerpt from gateway/delivery.py
# DeliveryRouter.deliver

# ===== lines 1-80 =====
"""
Delivery routing for cron job outputs and agent responses.

Routes messages to the appropriate destination based on:
- Explicit targets (e.g., "telegram:123456789")
- Platform home channels (e.g., "telegram" → home channel)
- Origin (back to where the job was created)
- Local (always saved to files)
"""

import logging
import os
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from hermes_cli.config import get_hermes_home

logger = logging.getLogger(__name__)

# Cap before gateway-level truncation of cron output for non-chunking platform
# delivery.  Telegram's hard API limit is 4096; the headroom covers the "full
# output saved to …" footer appended on truncation.  Adapters that split long
# messages natively (BasePlatformAdapter.splits_long_messages) bypass this
# entirely — the adapter chunks in its own send() and the full output is
# preserved.
MAX_PLATFORM_OUTPUT = 4000

# Matches strings that are *only* a "silence" narration with optional markdown
# wrappers. Covers: *(silent)*, _silent_, `silent`, ~silent~, (silent), silent,
# 🔇, a bare ".", "…", and the whitespace/marker-padded variants seen in the
# wild. Anchored to start/end so substantive messages that merely *contain* the
# word "silent" are never matched.
_SILENCE_NARRATION = re.compile(
    r'^[\s*_~`]*\(?\s*(silent|silence|no\s+response|no\s+reply)\s*\.?\)?[\s*_~`]*$'
    r'|^[\s*_~`]*[\U0001F507\.\u2026]+[\s*_~`]*$',
    re.IGNORECASE,
)


def _is_silence_narration(content: Optional[str]) -> bool:
    """Return True when ``content`` is *only* a silence-narration token.

    Length-guarded (real messages are longer) and anchored to the whole string
    so legitimate prose like "The deployment ran silently" or "Silence is
    golden — here is the plan..." is never flagged.
    """
    if not content:
        return False
    stripped = content.strip()
    if not stripped or len(stripped) > 64:  # length guard
        return False
    return bool(_SILENCE_NARRATION.match(stripped))

from .config import Platform, GatewayConfig
from .session import SessionSource
from .dead_targets import DeadTargetRegistry


def looks_like_telegram_private_chat_id(chat_id: Optional[str]) -> bool:
    """True when ``chat_id`` is a positive int — Telegram's private-chat shape.

    Telegram private chats use positive chat IDs; groups/channels/supergroups
    use negative IDs. This is the single source of truth for that heuristic,
    reused by the handoff seed path in ``gateway/run.py`` so handoff-created
    DM topics key the same way as inbound DM-topic messages.
    """
    if chat_id is None:
        return False
    try:
        return int(chat_id) > 0
    except (TypeError, ValueError):
        return False


def _looks_like_int(value: Optional[str]) -> bool:
    if value is None:
        return False

# ===== lines 222-320 =====
class DeliveryRouter:
    """
    Routes messages to appropriate destinations.
    
    Handles the logic of resolving delivery targets and dispatching
    messages to the right platform adapters.
    """
    
    def __init__(self, config: GatewayConfig, adapters: Dict[Platform, Any] = None,
                 dead_targets: Optional[DeadTargetRegistry] = None):
        """
        Initialize the delivery router.
        
        Args:
            config: Gateway configuration
            adapters: Dict mapping platforms to their adapter instances
            dead_targets: Optional shared registry of confirmed-unreachable
                targets.  When omitted, a profile-local registry is created.
        """
        self.config = config
        self.adapters = adapters or {}
        self.output_dir = get_hermes_home() / "cron" / "output"
        self.dead_targets = dead_targets or DeadTargetRegistry()
    
    async def deliver(
        self,
        content: str,
        targets: List[DeliveryTarget],
        job_id: Optional[str] = None,
        job_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deliver content to all specified targets.
        
        Args:
            content: The message/output to deliver
            targets: List of delivery targets
            job_id: Optional job ID (for cron jobs)
            job_name: Optional job name
            metadata: Additional metadata to include
        
        Returns:
            Dict with delivery results per target
        """
        results = {}
        
        for target in targets:
            # Skip targets we've already proven permanently unreachable
            # (deleted group, blocked/kicked bot, deactivated user). Re-sending
            # to them on every tick wastes a send against flood control and
            # spams logs. Self-healing: a later successful send clears the flag.
            # LOCAL/origin-without-chat targets are never dead-tracked.
            if (
                target.platform != Platform.LOCAL
                and target.chat_id
                and self.dead_targets.is_dead(target.platform.value, target.chat_id)
            ):
                logger.info(
                    "Skipping delivery to known-dead target %s:%s "
                    "(send to it again to clear)",
                    target.platform.value, target.chat_id,
                )
                results[target.to_string()] = {
                    "success": False,
                    "skipped": "dead_target",
                    "error": "target previously confirmed unreachable",
                }
                continue
            try:
                if target.platform == Platform.LOCAL:
                    result = self._deliver_local(content, job_id, job_name, metadata)
                else:
                    result = await self._deliver_to_platform(target, content, metadata)
                    # Successful platform delivery — clear any stale dead flag.
                    if target.chat_id and not _send_result_failed(result):
                        self.dead_targets.clear(target.platform.value, target.chat_id)
                
                results[target.to_string()] = {
                    "success": True,
                    "result": result
                }
            except Exception as e:
                # A hard failure raises here. If the platform reported a
                # whole-chat death, record it so future deliveries short-circuit.
                if target.platform != Platform.LOCAL and target.chat_id:
                    dead_kind = _classify_dead_from_error_text(str(e))
                    if dead_kind:
                        self.dead_targets.mark_dead(
                            target.platform.value, target.chat_id,
                            reason=f"{dead_kind}: {str(e)[:120]}",
                        )
                results[target.to_string()] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    

